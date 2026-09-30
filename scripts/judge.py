#!/usr/bin/env python3
"""Blind AI grading with a judge from a different model family than every contestant.

For every run under runs/<label>/, the judge sees: the task prompt, the source material,
the answer-key notes and the output. It never sees which profile or model wrote it, and
outputs are graded in shuffled order. Each output is graded `passes` times (default 2) at
temperature 0; report.py averages the passes.

Usage: OPENROUTER_API_KEY=... python3 scripts/judge.py [--label main] [--force]
"""
import argparse, json, os, random, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config/bench.json").read_text())
TASKS = {t["id"]: t for t in json.loads((ROOT / "tasks/tasks.json").read_text())["tasks"]}
KEY = json.loads((ROOT / "tasks/answer_keys.json").read_text())
INPUTS = ROOT / "tasks/inputs"

RUBRIC = """Score the OUTPUT on five criteria, each an integer from 1 (poor) to 5 (excellent):
- facts: every claim is traceable to the SOURCE MATERIAL; nothing invented. If ANY specification, number, price, date, name, quote or claim is not supported by the source, list it in invented_facts and score facts no higher than 2.
- complete: every part the task asked for is present.
- reader: tone, framing and benefits fit the reader named in the task.
- ready: a product marketer could send it with only light edits.
- format: length limits, item counts and structure are exactly as asked.
Be strict and consistent. Judge only against the task, the source and the reference notes.
Reply with JSON only:
{"facts": n, "complete": n, "reader": n, "ready": n, "format": n, "invented_facts": ["..."], "notes": "one or two sentences"}"""


def call_judge(prompt, key):
    body = {"model": CFG["judge"]["model"], "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": "You are a strict, fair grader of product marketing work."},
                         {"role": "user", "content": prompt}]}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            data = json.load(urllib.request.urlopen(req, timeout=180))
            text = data["choices"][0]["message"]["content"]
            text = text[text.find("{"): text.rfind("}") + 1]
            return json.loads(text), data.get("usage", {})
        except Exception as e:
            if attempt == 3:
                raise
            print(f"   retry after error: {e}")
            time.sleep(5 * (attempt + 1))


def build_prompt(rdir, task_id):
    t = TASKS[task_id]
    sources = "\n\n".join(f"--- {s} ---\n{(INPUTS / s).read_text()}" for s in t["sources"])
    output = (rdir / "response.md").read_text() if (rdir / "response.md").exists() else ""
    if t.get("output_file"):
        f = rdir / "workspace" / t["output_file"]
        saved = f.read_text() if f.exists() else "(FILE NOT SAVED)"
        output = f"Saved file {t['output_file']}:\n{saved}\n\nFinal reply:\n{output}"
    ref = KEY.get(task_id, {})
    notes = ref.get("judge_notes") or json.dumps(ref.get("expected", {}), indent=1)
    if task_id == "T4":
        notes = "Expected answers:\n" + json.dumps(ref["expected"], indent=1)
    return (f"{RUBRIC}\n\n=== TASK ===\n{t['prompt']}\n\n=== SOURCE MATERIAL ===\n{sources}\n\n"
            f"=== REFERENCE NOTES FOR THE GRADER ===\n{notes}\n\n=== OUTPUT TO GRADE ===\n{output or '(EMPTY OUTPUT)'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="main")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    key = os.environ.get("OPENROUTER_API_KEY") or sys.exit("export OPENROUTER_API_KEY first")
    runs = sorted((ROOT / "runs" / a.label).glob("*/T*/r*"))
    passes = CFG["judge"]["passes"]
    jobs = [(r, p) for r in runs for p in range(1, passes + 1)
            if a.force or not (r / f"judge_pass{p}.json").exists()]
    random.shuffle(jobs)  # blind order: profiles and tasks interleaved
    spent = 0.0
    for i, (rdir, p) in enumerate(jobs, 1):
        print(f"[{i}/{len(jobs)}] grading item {abs(hash(str(rdir))) % 10**6:06d} pass {p}", flush=True)
        res, usage = call_judge(build_prompt(rdir, rdir.parent.name), key)
        cost = usage.get("cost")
        if cost is None:
            cost = (usage.get("prompt_tokens", 0) * CFG["judge"]["price_in"] + usage.get("completion_tokens", 0) * CFG["judge"]["price_out"]) / 1e6
        spent += cost
        res["_judge_model"] = CFG["judge"]["model"]
        res["_judge_cost_usd"] = round(cost, 6)
        (rdir / f"judge_pass{p}.json").write_text(json.dumps(res, indent=2))
    print(f"Done. Judge spend this session: ${spent:.4f}")


if __name__ == "__main__":
    main()
