#!/usr/bin/env python3
"""Human audit of the judge's invented-fact flags on the re-graded T4/T6 outputs.

I mark each flag in results/judge_flag_audit.csv as real, borderline or wrong.
This script reports how many flags hold up, whether flags found by all three judge
passes are more reliable than flags found by one or two, and how many outputs would
change usable status if only confirmed flags triggered the invented-fact gate.

Usage: python3 scripts/flag_audit.py
"""
import csv, json, statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CRIT = ["facts", "complete", "reader", "ready", "format"]
meta = json.loads((ROOT / "results/.flag_audit_map.json").read_text())
rows = list(csv.DictReader((ROOT / "results/judge_flag_audit.csv").open(encoding="utf-8-sig")))


def verdict(v):
    v = (v or "").strip().lower()
    return {"r": "real", "b": "borderline", "w": "wrong"}.get(v[:1], "")


marked = [(r, verdict(r["verdict"])) for r in rows if verdict(r["verdict"])]
if not marked:
    raise SystemExit("No verdicts yet: fill the verdict column with real, borderline or wrong.")
n = len(marked)
count = defaultdict(int)
for _, v in marked:
    count[v] += 1
print(f"Judge fact flags audited: {n} of {len(rows)}")
print(f"  real {count['real']} ({100 * count['real'] / n:.0f}%), borderline {count['borderline']} "
      f"({100 * count['borderline'] / n:.0f}%), wrong {count['wrong']} ({100 * count['wrong'] / n:.0f}%)")

by_passes = defaultdict(lambda: defaultdict(int))
for r, v in marked:
    by_passes["3 of 3" if meta[r["flag_id"]]["passes_flagged"] == 3 else "1-2 of 3"][v] += 1
for k, c in by_passes.items():
    tot = sum(c.values())
    print(f"  flagged by {k} passes: {tot} flags, {c['real']} real ({100 * c['real'] / tot:.0f}%)")

# per output: does the invented-fact gate still hold?
outs = defaultdict(list)
for r, v in marked:
    outs[meta[r["flag_id"]]["run"]].append(v)
changed = {"strict": 0, "lenient": 0}
for run, vs in outs.items():
    passes = [json.loads(p.read_text()) for p in sorted((ROOT / run).glob("judge_pass*.json"))]
    j = {c: st.mean(float(p[c]) for p in passes) for c in CRIT}
    gated_total = sum(j.values()) - j["facts"] + min(j["facts"], 2.0)
    raw_total = sum(j.values())
    for mode, keep in (("strict", {"real", "borderline"}), ("lenient", {"real"})):
        gate = any(v in keep for v in vs)
        usable_now = False                      # every flagged output is gated today
        usable_after = (not gate) and raw_total >= 20
        if usable_after != usable_now:
            changed[mode] += 1
print(f"Outputs with flags: {len(outs)}. Would become usable if only confirmed flags gated:")
print(f"  real or borderline gate: {changed['strict']}   real-only gate: {changed['lenient']}")
(ROOT / "results/judge_flag_audit.txt").write_text(
    f"{n} flags audited; real {count['real']}, borderline {count['borderline']}, wrong {count['wrong']}; "
    f"usable changes: {changed['strict']} (real+borderline gate), {changed['lenient']} (real-only gate)\n")
