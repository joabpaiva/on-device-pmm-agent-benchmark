#!/usr/bin/env python3
"""Aggregate runs, scripted checks and judge scores into the CSV tables used on the results slides.

Outputs (results/):
  per_run_<label>.csv     every run with all metrics, checks and scores
  scoreboard.csv          slide "Quality scoreboard"   (median score of 25, spread across runs)
  efficiency.csv          slide "Cost, speed and trust"
  phase2.csv              slide "On-device reality check" (pmm-a hosted vs pmm-d laptop)
  human_regrade.csv       blind sheet for the human re-grade of T4 and T6 (created once; fill it in)

Usage: python3 scripts/report.py [--label main] [--offline-label offline]
"""
import argparse, csv, hashlib, json, statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config/bench.json").read_text())
OUT = ROOT / "results"
CRIT = ["facts", "complete", "reader", "ready", "format"]
TASK_IDS = ["T1", "T2", "T3", "T4", "T5", "T6"]


MISSING_CHECKS = []


def score(v):
    """Judge scores should be integers 1-5; tolerate '4/5' or '4.0', clamp anything else."""
    try:
        v = float(str(v).split("/")[0])
    except (TypeError, ValueError):
        return 1.0
    return min(5.0, max(1.0, v))


def load(label):
    rows = []
    for rdir in sorted((ROOT / "runs" / label).glob("*/T*/r*")):
        m = rdir / "metrics.json"
        if not m.exists():
            continue
        r = json.loads(m.read_text())
        r["_dir"] = rdir
        r["checks"] = json.loads((rdir / "checks.json").read_text()) if (rdir / "checks.json").exists() else {}
        passes = [json.loads(p.read_text()) for p in sorted(rdir.glob("judge_pass*.json"))]
        if not (rdir / "checks.json").exists():
            MISSING_CHECKS.append(str(rdir.relative_to(ROOT)))
        r["judged"] = bool(passes)
        if passes:
            for c in CRIT:
                r[c] = st.mean(score(p.get(c)) for p in passes)
            r["invented"] = st.mean(len(p.get("invented_facts") or []) for p in passes)
            r["judge_cost"] = sum(p.get("_judge_cost_usd", 0) for p in passes)
        gates = []
        if r.get("invented", 0) > 0:                   # any judge pass found an invented fact
            r["facts"] = min(r.get("facts", 1), 2.0); gates.append("invented fact")
        ch = r["checks"]
        if r["task"] == "T6" and not ch.get("file_saved", True):
            r["complete"] = min(r.get("complete", 1), 2.0); gates.append("file not saved")
        if r["task"] == "T2" and ch.get("used_unverified_rumor"):
            r["facts"] = min(r.get("facts", 1), 2.0); gates.append("used unverified rumor")
        if r["task"] == "T4" and not ch.get("q5_declined", True):
            gates.append("Q5 fabricated")
        r["total"] = round(sum(r.get(c, 0) for c in CRIT), 2) if passes else None
        r["gates"] = gates
        r["usable"] = bool(passes) and r["total"] >= 20 and not gates
        if CFG["profiles"][r["profile"]]["local"] and CFG.get("electricity_usd_per_kwh") and r.get("energy_wh") not in ("", None):
            r["cost_usd"] = round(float(r["energy_wh"]) / 1000 * CFG["electricity_usd_per_kwh"], 6)
        rows.append(r)
    return rows


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def mean_of(rows, key, nd=2):
    vals = [num(r.get(key)) for r in rows]
    vals = [v for v in vals if v is not None]
    return round(st.mean(vals), nd) if vals else ""


def fmt_med(vals):
    if not vals:
        return ""
    return f"{st.median(vals):.1f} ({max(vals) - min(vals):.1f})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="main")
    ap.add_argument("--offline-label", default="offline")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    rows = load(a.label)
    if not rows:
        raise SystemExit(f"No runs found in runs/{a.label}/")
    profiles = [p for p in CFG["profiles"] if any(r["profile"] == p for r in rows)]
    by = lambda p, t=None: [r for r in rows if r["profile"] == p and (t is None or r["task"] == t)]

    # per-run
    flat_keys = ["profile", "model", "task", "run", "started_at", "exit_code", "error", "duration_s", "ttft_s",
                 "tokens_in", "tokens_out", "tokens_per_s", "cost_usd", "tool_calls", "tool_errors",
                 "output_file_saved", "files_written", "energy_wh", "avg_power_w", "peak_llama_rss_gb", "remote_endpoints"] + CRIT + ["total", "invented", "usable"]
    with (OUT / f"per_run_{a.label}.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(flat_keys + ["gates", "checks"])
        for r in rows:
            w.writerow([r.get(k, "") for k in flat_keys] + ["; ".join(r["gates"]), json.dumps(r["checks"])])

    # scoreboard
    frontier = "pmm-c"
    avgs = {}
    with (OUT / "scoreboard.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Task"] + [f"{p} {CFG['profiles'][p]['class']}" for p in profiles])
        for t in TASK_IDS:
            w.writerow([t] + [fmt_med([r["total"] for r in by(p, t) if r["total"] is not None]) for p in profiles])
        for p in profiles:
            meds = [st.median([r["total"] for r in by(p, t) if r["total"] is not None]) for t in TASK_IDS
                    if any(r["total"] is not None for r in by(p, t))]
            avgs[p] = st.mean(meds) if meds else None
        w.writerow(["Average (of 25)"] + [f"{avgs[p]:.1f}" if avgs[p] is not None else "" for p in profiles])
        fr = avgs.get(frontier)
        w.writerow(["% of frontier score"] + [f"{100 * avgs[p] / fr:.0f}%" if fr and avgs[p] is not None else "" for p in profiles])
        w.writerow(["Usable outputs"] + [f"{sum(r['usable'] for r in by(p))} of {len(by(p))}" for p in profiles])

    # efficiency
    def eff(p):
        rs = by(p)
        usable = sum(r["usable"] for r in rs)
        total_cost = sum(num(r.get("cost_usd")) or 0 for r in rs)
        t4, t6 = by(p, "T4"), by(p, "T6")
        calls = sum(int(r.get("tool_calls") or 0) for r in t6)
        errs = sum(int(r.get("tool_errors") or 0) for r in t6)
        spreads = []
        for t in TASK_IDS:
            v = [r["total"] for r in by(p, t) if r["total"] is not None]
            if len(v) > 1:
                spreads.append(max(v) - min(v))
        return {
            "Cost per task ($)": mean_of(rs, "cost_usd", 6),
            "Cost per usable output ($)": round(total_cost / usable, 5) if usable else "no usable output",
            "Latency per task (s)": mean_of(rs, "duration_s"),
            "Time to first output (s)": mean_of(rs, "ttft_s"),
            "Tokens per second": mean_of(rs, "tokens_per_s"),
            "Hallucinations (total)": round(sum(r.get("invented", 0) for r in rs), 1),
            "T4 Q5 declined correctly": f"{sum(1 for r in t4 if r['checks'].get('q5_declined'))} of {len(t4)}",
            "T6 cells correct (of 24)": round(st.mean(r["checks"].get("cells_correct", 0) for r in t6), 1) if t6 else "",
            "T6 gaps marked (of 3)": round(st.mean(r["checks"].get("gaps_marked", 0) for r in t6), 1) if t6 else "",
            "T6 tool calls succeeded (%)": round(100 * (calls - errs) / calls) if calls else "no tool calls",
            "Score spread across runs (avg)": round(st.mean(spreads), 2) if spreads else "",
            "Energy per task (Wh)": mean_of(rs, "energy_wh", 4),
            "Peak model memory (GB)": max([num(r.get("peak_llama_rss_gb")) or 0 for r in rs]) or "",
        }
    effs = {p: eff(p) for p in profiles}
    with (OUT / "efficiency.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Metric"] + [f"{p} {CFG['profiles'][p]['class']}" for p in profiles])
        for k in next(iter(effs.values())):
            w.writerow([k] + [effs[p][k] for p in profiles])

    # phase 2
    if "pmm-a" in profiles and "pmm-d" in profiles:
        d = sorted(by("pmm-d"), key=lambda r: r["started_at"])
        k = max(1, len(d) // 4)
        first, last = [num(r.get("tokens_per_s")) for r in d[:k]], [num(r.get("tokens_per_s")) for r in d[-k:]]
        first, last = [v for v in first if v], [v for v in last if v]
        drift = f"{st.mean(first):.1f} -> {st.mean(last):.1f} tok/s" if first and last else ""
        off = load(a.offline_label) if (ROOT / "runs" / a.offline_label).exists() else []
        off_d = [r for r in off if r["profile"] == "pmm-d"]
        endpoints = sorted({e for r in d + off_d for e in (r.get("remote_endpoints") or "").split(";") if e})
        with (OUT / "phase2.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Measure", "pmm-a hosted", "pmm-d laptop", "Matches or differs?", "Why"])
            w.writerow(["Average quality (of 25)", f"{avgs['pmm-a']:.1f}" if avgs.get("pmm-a") else "", f"{avgs['pmm-d']:.1f}" if avgs.get("pmm-d") else "", "", ""])
            w.writerow(["Latency per task (s)", effs["pmm-a"]["Latency per task (s)"], effs["pmm-d"]["Latency per task (s)"], "", ""])
            w.writerow(["Tokens per second", effs["pmm-a"]["Tokens per second"], effs["pmm-d"]["Tokens per second"], "", ""])
            w.writerow(["Works with Wi-Fi off", "No", (f"{sum(1 for r in off_d if str(r['exit_code']) == '0')} of {len(off_d)} runs completed" if off_d else "run --label offline"), "", ""])
            w.writerow(["Connections off-device during runs", "All task data (by design)", ("none observed" if not endpoints else "; ".join(endpoints)), "", ""])
            w.writerow(["Energy per task (Wh)", "Not measurable", effs["pmm-d"]["Energy per task (Wh)"], "", ""])
            w.writerow(["Peak model memory (GB)", "N/A", effs["pmm-d"]["Peak model memory (GB)"], "", ""])
            w.writerow(["Speed, first vs last runs", "N/A", drift, "", ""])
            w.writerow(["Cost per task ($)", effs["pmm-a"]["Cost per task ($)"], effs["pmm-d"]["Cost per task ($)"], "", ""])

    # human re-grade sheet (blind): outputs copied to results/regrade/<id>.md, new runs appended on each report
    hr, mp_path, rg_dir = OUT / "human_regrade.csv", OUT / ".regrade_map.json", OUT / "regrade"
    rg_dir.mkdir(exist_ok=True)
    mp = json.loads(mp_path.read_text()) if mp_path.exists() else {}
    existing = list(csv.DictReader(hr.open(encoding="utf-8-sig"))) if hr.exists() else []
    have = {h["blind_id"] for h in existing}
    added = 0
    for r in sorted((r for r in rows if r["task"] in ("T4", "T6")), key=lambda r: hashlib.sha1(str(r["_dir"]).encode()).hexdigest()):
        bid = hashlib.sha1(str(r["_dir"].relative_to(ROOT)).encode()).hexdigest()[:8]
        src = r["_dir"] / ("workspace/outputs/t6_matrix.md" if r["task"] == "T6" else "deliverable.md")
        (rg_dir / f"{bid}.md").write_text(f"# {r['task']} output {bid}\n\n" + (src.read_text() if src.exists() else "(no output file)"))
        mp[bid] = str(r["_dir"].relative_to(ROOT))
        if bid not in have:
            existing.append({"blind_id": bid, "task": r["task"], "file": f"results/regrade/{bid}.md", **{c: "" for c in CRIT}, "notes": ""})
            added += 1
    mp_path.write_text(json.dumps(mp, indent=1))
    with hr.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["blind_id", "task", "file"] + CRIT + ["notes"], extrasaction="ignore")
        w.writeheader(); w.writerows(existing)
    if added:
        print(f"human_regrade.csv: {added} new outputs to grade (open the files in results/regrade/; profiles stay hidden)")
    pairs = []
    for h in existing:
        if all(h.get(c) for c in CRIT):
            human = sum(score(h[c]) for c in CRIT)
            r = next((r for r in rows if str(r["_dir"].relative_to(ROOT)) == mp.get(h["blind_id"])), None)
            if r and r["total"] is not None:
                pairs.append(abs(human - r["total"]))
    if pairs:
        agree = sum(1 for d in pairs if d <= 2) / len(pairs)
        print(f"Human vs judge: {len(pairs)} outputs, {100 * agree:.0f}% within 2 points of 25, mean gap {st.mean(pairs):.1f}")
        (OUT / "judge_agreement.txt").write_text(f"{len(pairs)} outputs; {100 * agree:.0f}% within 2 points; mean gap {st.mean(pairs):.1f}\n")

    if MISSING_CHECKS:
        print(f"WARNING: {len(MISSING_CHECKS)} runs have no checks.json, so their gates were not applied. Run scripts/check.py first.")
    unjudged = sum(1 for r in rows if not r["judged"])
    print(f"Wrote results/ for {len(rows)} runs ({unjudged} not yet judged). Profiles: {', '.join(profiles)}")
    for name in ("scoreboard.csv", "efficiency.csv", "phase2.csv"):
        p = OUT / name
        if p.exists():
            print(f"\n== {name}")
            print(p.read_text())


if __name__ == "__main__":
    main()
