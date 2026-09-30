#!/usr/bin/env python3
"""Blind AI grading with a judge from a different model family than every contestant.

For every run under runs/<label>/, the judge sees: the task prompt, the source material,
the answer-key notes and the output. It never sees which profile or model wrote it, and
outputs are graded in shuffled order. Each output is graded `passes` times (3 in config/bench.json) at
temperature 0; report.py averages the passes.

Usage: python3 scripts/judge.py [--label main] [--force]
"""
import argparse, json, os, random, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import build_deliverable  # noqa: E402

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


def valid(res):
    return all(isinstance(res.get(c), int) and 1 <= res[c] <= 5 for c in ("facts", "complete", "reader", "ready", "format"))


def build_prompt(rdir, task_id):
    t = TASKS[task_id]
    sources = "\n\n".join(f"--- {s} ---\n{(INPUTS / s).read_text()}" for s in t["sources"])
    output = build_deliverable(rdir)  # the agent's reply plus any files it wrote
    if t.get("output_file") and not (rdir / "workspace" / t["output_file"]).exists():
        output += f"\n\n(NOTE FOR GRADER: the required file {t['output_file']} was NOT saved.)"
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
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:  # fall back to the key setup_profiles.sh saved in pmm-a's .env
        env = Path.home() / ".hermes/profiles/pmm-a/.env"
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("OPENROUTER_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        sys.exit("No OpenRouter key found. Run profiles/setup_profiles.sh first, or export OPENROUTER_API_KEY.")
    runs = sorted((ROOT / "runs" / a.label).glob("*/T*/r*"))
    passes = CFG["judge"]["passes"]
    jobs = [(r, p) for r in runs for p in range(1, passes + 1)
            if a.force or not (r / f"judge_pass{p}.json").exists()]
    random.shuffle(jobs)  # blind order: profiles and tasks interleaved
    spent = 0.0
    for i, (rdir, p) in enumerate(jobs, 1):
        print(f"[{i}/{len(jobs)}] grading item {abs(hash(str(rdir))) % 10**6:06d} pass {p}", flush=True)
        prompt = build_prompt(rdir, rdir.parent.name)
        res, usage = call_judge(prompt, key)
        if not valid(res):   # one retry if a score is missing or not an integer 1-5
            res, usage2 = call_judge(prompt, key)
            usage = {k: usage.get(k, 0) + usage2.get(k, 0) for k in set(usage) | set(usage2) if isinstance(usage.get(k, 0), (int, float))}
            if not valid(res):
                print(f"   WARNING: judge returned invalid scores for {rdir.relative_to(ROOT)}; kept as-is")
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
