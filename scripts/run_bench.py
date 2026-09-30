#!/usr/bin/env python3
"""Run the benchmark: every task x every run x every profile, through the Hermes CLI.

Each run gets a fresh working folder and a fresh Hermes session (one-shot), so no run can
see another. Hermes is called with --format stream-json, which gives timings, token counts
and tool calls without scraping terminal output.

Examples
  python3 scripts/run_bench.py --profiles pmm-a,pmm-b,pmm-c                 # Phase 1
  python3 scripts/run_bench.py --profiles pmm-d --energy                    # Phase 2 (sudo -v first)
  python3 scripts/run_bench.py --profiles pmm-d --label offline --runs 1    # Wi-Fi off rerun
  python3 scripts/run_bench.py --profiles pmm-a --tasks T4 --runs 1         # smoke test

Standard library only.
"""
import argparse, csv, json, os, re, shutil, signal, subprocess, sys, threading, time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = json.loads((ROOT / "tasks/tasks.json").read_text())["tasks"]
CFG = json.loads((ROOT / "config/bench.json").read_text())
INPUTS = ROOT / "tasks/inputs"

CSV_FIELDS = ["label", "profile", "model", "task", "run", "started_at", "exit_code", "error",
              "duration_s", "ttft_s", "tokens_in", "tokens_out", "cache_read", "tokens_per_s", "cost_usd",
              "tool_calls", "tool_errors", "output_file_saved", "energy_wh", "avg_power_w",
              "peak_llama_rss_gb", "remote_endpoints"]


def build_query(task):
    q = task["prompt"]
    for name in task["attachments"]:
        q += f"\n\n---\nAttached file: {name}\n---\n" + (INPUTS / name).read_text()
    return q


# ---------------- on-device monitors (macOS) ----------------
class Monitor(threading.Thread):
    """Samples peak llama-server memory and any non-loopback network endpoints of the agent processes."""

    def __init__(self, root_pid, watch_net):
        super().__init__(daemon=True)
        self.root_pid, self.watch_net = root_pid, watch_net
        self.stop_evt = threading.Event()
        self.peak_rss_kb = 0
        self.endpoints = set()
        self.llama_pid = None
        sj = Path.home() / ".hermes/runtimes/llamacpp/server.json"
        if sj.exists():
            try:
                self.llama_pid = json.loads(sj.read_text()).get("pid")
            except Exception:
                pass

    def descendants(self, pid):
        out, frontier = {pid}, [pid]
        while frontier:
            p = frontier.pop()
            try:
                kids = subprocess.run(["pgrep", "-P", str(p)], capture_output=True, text=True).stdout.split()
            except Exception:
                kids = []
            for k in kids:
                k = int(k)
                if k not in out:
                    out.add(k); frontier.append(k)
        return out

    def run(self):
        while not self.stop_evt.is_set():
            if self.llama_pid:
                r = subprocess.run(["ps", "-o", "rss=", "-p", str(self.llama_pid)], capture_output=True, text=True).stdout.strip()
                if r.isdigit():
                    self.peak_rss_kb = max(self.peak_rss_kb, int(r))
            if self.watch_net:
                pids = self.descendants(self.root_pid)
                if self.llama_pid:
                    pids.add(self.llama_pid)
                r = subprocess.run(["lsof", "-nP", "-i", "-a", "-p", ",".join(map(str, pids))],
                                   capture_output=True, text=True).stdout
                for line in r.splitlines()[1:]:
                    m = re.search(r"->(\S+)", line)
                    if m:
                        host = m.group(1).rsplit(":", 1)[0].strip("[]")
                        if host not in ("127.0.0.1", "::1", "localhost"):
                            self.endpoints.add(m.group(1))
            self.stop_evt.wait(1.0)


def start_powermetrics():
    try:
        return subprocess.Popen(["sudo", "-n", "powermetrics", "-i", "500", "--samplers", "cpu_power,gpu_power,ane_power"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except Exception as e:
        print(f"   powermetrics not started: {e}")
        return None


def stop_powermetrics(proc):
    if not proc:
        return None
    subprocess.run(["sudo", "-n", "kill", "-INT", str(proc.pid)], capture_output=True)
    try:
        out, err = proc.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill(); out, err = proc.communicate()
    vals = [int(v) for v in re.findall(r"Combined Power \(CPU \+ GPU \+ ANE\):\s*(\d+)\s*mW", out)]
    if not vals:
        if err.strip():
            print("   powermetrics:", err.strip().splitlines()[-1])
        return None
    return sum(vals) / len(vals) / 1000.0  # average watts


# ---------------- one run ----------------
def run_once(label, profile, task, run_idx, energy, timeout):
    pcfg = CFG["profiles"][profile]
    rdir = ROOT / "runs" / label / profile / task["id"] / f"r{run_idx}"
    if rdir.exists():
        shutil.rmtree(rdir)
    ws = rdir / "workspace"
    (ws / "outputs").mkdir(parents=True)
    for rel in task["workspace_files"]:
        dst = ws / "inputs" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(INPUTS / rel, dst)
    query_file = rdir / "query.txt"
    query_file.write_text(build_query(task))

    cmd = ["hermes", "-p", profile, "chat", "--query-file", str(query_file), "--format", "stream-json",
           "-t", CFG["toolsets"], "--source", "tool", "--yolo", "--max-turns", "30"]
    started = datetime.now().isoformat(timespec="seconds")
    pm = start_powermetrics() if energy else None
    t0 = time.time()
    proc = subprocess.Popen(cmd, cwd=ws, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    mon = Monitor(proc.pid, watch_net=pcfg["local"]) if pcfg["local"] else None
    if mon:
        mon.start()

    events, first_text_ts, init_ts, texts = [], None, None, []
    tool_calls = tool_errors = 0
    result = None
    killer = threading.Timer(timeout, lambda: proc.kill())
    killer.start()
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        events.append(ev)
        typ = ev.get("type")
        if typ == "system" and init_ts is None:
            init_ts = ev.get("timestamp")
        elif typ == "text":
            if first_text_ts is None:
                first_text_ts = ev.get("timestamp")
            texts.append(ev.get("text", ""))
        elif typ == "tool_use":
            tool_calls += 1
        elif typ == "tool_result" and ev.get("is_error"):
            tool_errors += 1
        elif typ == "result":
            result = ev
    proc.wait()
    killer.cancel()
    wall = time.time() - t0
    stderr = proc.stderr.read()
    if mon:
        mon.stop_evt.set(); mon.join(timeout=3)
    avg_w = stop_powermetrics(pm)

    final_text = (result or {}).get("text") or "".join(texts)
    (rdir / "response.md").write_text(final_text or "")
    (rdir / "events.jsonl").write_text("\n".join(json.dumps(e) for e in events))
    if stderr.strip():
        (rdir / "stderr.txt").write_text(stderr)

    tok = (result or {}).get("tokens") or {}
    # Hermes reports cached prompt tokens separately; count them all as input. Cost prices every
    # prompt token at the list input rate (cache discounts ignored), so cost is an upper bound.
    tin = (tok.get("input") or 0) + (tok.get("cache_read") or 0) + (tok.get("cache_write") or 0)
    tout = tok.get("output") or 0
    dur = ((result or {}).get("duration_ms") or wall * 1000) / 1000.0
    ttft = (first_text_ts - init_ts) / 1000.0 if (first_text_ts and init_ts) else None
    gen_time = dur - (ttft or 0)
    out_file = task.get("output_file")
    row = {
        "label": label, "profile": profile, "model": pcfg["model"], "task": task["id"], "run": run_idx,
        "started_at": started,
        "exit_code": (result or {}).get("exit_code", proc.returncode),
        "error": (result or {}).get("error") or ("timeout/no result" if result is None else ""),
        "duration_s": round(dur, 2), "ttft_s": round(ttft, 2) if ttft is not None else "",
        "tokens_in": tin, "tokens_out": tout, "cache_read": tok.get("cache_read") or 0,
        "tokens_per_s": round(tout / gen_time, 1) if tout and gen_time > 0 else "",
        "cost_usd": round(tin * pcfg["price_in"] / 1e6 + tout * pcfg["price_out"] / 1e6, 6),
        "tool_calls": tool_calls, "tool_errors": tool_errors,
        "output_file_saved": (ws / out_file).exists() if out_file else "",
        "energy_wh": round(avg_w * wall / 3600, 4) if avg_w else "",
        "avg_power_w": round(avg_w, 1) if avg_w else "",
        "peak_llama_rss_gb": round(mon.peak_rss_kb / 1024 / 1024, 2) if mon and mon.peak_rss_kb else "",
        "remote_endpoints": ";".join(sorted(mon.endpoints)) if mon else "",
    }
    (rdir / "metrics.json").write_text(json.dumps(row, indent=2))
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles", default="pmm-a,pmm-b,pmm-c")
    ap.add_argument("--tasks", default="T1,T2,T3,T4,T5,T6")
    ap.add_argument("--runs", type=int, default=CFG["runs_per_task"])
    ap.add_argument("--label", default="main", help="results group, e.g. main | offline | battery")
    ap.add_argument("--energy", action="store_true", help="measure SoC power with powermetrics (run `sudo -v` first)")
    ap.add_argument("--cooldown", type=float, default=0, help="seconds to wait between runs")
    a = ap.parse_args()

    profiles = a.profiles.split(",")
    for p in profiles:
        if p not in CFG["profiles"]:
            sys.exit(f"unknown profile {p}")
        if CFG["profiles"][p]["model"] == "SET_AFTER_DOWNLOAD":
            sys.exit(f"{p}: run scripts/set_local_model.py first")
    tasks = [t for t in TASKS if t["id"] in a.tasks.split(",")]

    out_csv = ROOT / "runs" / a.label / "runs.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    new = not out_csv.exists()
    total = len(profiles) * len(tasks) * a.runs
    n = 0
    with out_csv.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if new:
            w.writeheader()
        for p in profiles:
            for r in range(1, a.runs + 1):          # round-robin tasks within each run round
                for t in tasks:
                    n += 1
                    print(f"[{n}/{total}] {a.label} {p} {t['id']} r{r} ...", flush=True)
                    row = run_once(a.label, p, t, r, a.energy, CFG["run_timeout_seconds"])
                    w.writerow(row); f.flush()
                    flag = "OK" if str(row["exit_code"]) == "0" else f"FAIL ({row['error']})"
                    print(f"     {flag}  {row['duration_s']}s  in={row['tokens_in']} out={row['tokens_out']}  ${row['cost_usd']}"
                          + (f"  {row['energy_wh']} Wh" if row["energy_wh"] else "")
                          + (f"  endpoints={row['remote_endpoints']}" if row["remote_endpoints"] else ""), flush=True)
                    if a.cooldown:
                        time.sleep(a.cooldown)
    print(f"\nDone. Rows appended to {out_csv.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
