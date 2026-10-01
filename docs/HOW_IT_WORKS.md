# How It Works

*Joab Paiva*

I built this benchmark to answer one question with measurements instead of assertions: **which everyday product marketing work can move from the cloud to the PC without losing quality, and what do you gain or give up when it does?**

This page explains how I set it up, how a run works, how I score the results, and where the numbers are approximate.

---

## The design in one paragraph

I created one product marketing agent in Hermes Agent (Nous Research) and cloned it into four profiles that differ only in the model behind them. I wrote six realistic PMM tasks, each designed to test a different capability, and froze the prompts. Every task runs three times on every profile, in a fresh session each time. A Python script drives Hermes through its own command line so every run is identical and precisely timed. Scoring combines rule-based checks, a blind AI judge from a different model family than any contestant, and my own re-grade of the two hardest tasks.

## The four agents

| Profile | Model | Where it runs | What it answers |
|---|---|---|---|
| `pmm-a` | Qwen3.5-9B | OpenRouter (hosted) | What can a laptop-sized model do? |
| `pmm-b` | Qwen3.5-27B | OpenRouter (hosted) | What does workstation-class memory buy? |
| `pmm-c` | Claude Sonnet 5.5 | OpenRouter (cloud) | What is the best available quality? |
| `pmm-d` | Qwen3.5-9B, 8-bit GGUF (Q8_0) | My MacBook Air, Hermes-installed llama.cpp (build 10964, Metal) | What changes on a real device? |

Design choices:
- **Same model generation for a and b**, so the only variable between them is size.
- **pmm-d is pmm-a on my laptop**, which isolates the on-device effect.
- **Neutral names** (`pmm-a` to `pmm-d`) so nothing in the output hints at which model wrote it.
- **A pinned local server.** Instead of letting the desktop app manage the local model, I launch the same llama.cpp engine Hermes installed with explicit settings (`scripts/start_local_server.sh`): full GPU offload, 64K context (the minimum Hermes accepts), thinking off, listening on localhost only. Every setting is on record and repeatable.
- **Identical setup:** same `SOUL.md`, memory off, background review off, reasoning effort `none`, file tools only. `profiles/setup_profiles.sh` applies all of it, so it is repeatable.

## The six tasks

All inputs are fictional products (Aurora 14, Vantage Pro 16, Summit X15) that I created for the test, and several contain deliberate traps.

| Task | PMM job | What it tests | Trap |
|---|---|---|---|
| T1 | Launch blog from a spec sheet | Grounded long-form writing | Any invented spec, price or benchmark counts as a fabrication |
| T2 | Competitive battlecard | Fair comparison, persuasion without fabrication | The brief contains an "unverified rumor" that must not be used |
| T3 | Executive summary of a white paper | Compression that keeps the fine print | 6 caveats buried in the paper must survive |
| T4 | Customer FAQ from product docs | Grounded answers, knowing when not to answer | Q5 (Ubuntu certification) has no answer in the docs |
| T5 | 3-email nurture sequence | Many constraints at once | Word limits, one CTA per email, no invented statistics |
| T6 | Competitive spec matrix | Tool use and multi-step agent work | 3 values are deliberately missing and must be marked "not stated" |

The prompts are in `tasks/tasks.json`, the source material in `tasks/inputs/`, and the expected answers in `tasks/answer_keys.json`.

## Why a script instead of chatting with each bot

The script does not replace the agent. It calls the same Hermes profiles through Hermes's own command line, the same agents I use in the Hermes app. I chose a script for the measured runs because running 72 chats by hand would weaken the results:

- **No carry-over:** every run is a brand-new session, so no answer can influence the next.
- **Exact timing:** Hermes reports timings and token counts directly, with no stopwatch.
- **Identical prompts:** the prompt is read from a file, byte for byte the same every time.
- **Reproducible:** anyone can rerun the same commands and compare.

For the demo, I run tasks live in the Hermes app to show the agent working. The script produces the numbers.

## What happens in one run

Each run is a single Hermes command:

```bash
hermes -p pmm-b chat --query-file query.txt --format stream-json -t file --source tool --yolo --max-turns 30
```

| Flag | Why I use it |
|---|---|
| `-p pmm-b` | Selects the agent: its SOUL.md, model and settings |
| `--query-file query.txt` | The frozen prompt, read from a file so it is identical every time |
| `--format stream-json` | Hermes reports each step as data: start, tool calls, first text, final answer, tokens, duration |
| `-t file` | Only file tools (read, write, search). No web, no terminal |
| `--source tool` | Keeps benchmark sessions out of my normal chat history |
| `--yolo` | Skips approval prompts, since no one is present to click. With only file tools, nothing risky can run |
| `--max-turns 30` | Caps an agent that gets stuck in a tool loop |

`scripts/run_bench.py` wraps that command. For every run it:

1. **Resets a scratch folder** at `/tmp/pmm-bench/work` and copies in the task's input files (only T6 needs them). The folder sits outside any git repository on purpose: Hermes tells the model which project folder it is in, and my smoke test showed that a folder name can leak into answers and confuse file paths. A fixed, neutral path keeps what the model sees identical for every run.
2. **Builds the prompt:** the frozen task prompt plus the source documents attached underneath.
3. **Launches Hermes** in that folder and reads the event stream as it arrives.
4. **Saves the full record** to `runs/<label>/<profile>/<task>/r<n>/`:
   - `query.txt`: exactly what the model received
   - `response.md`: its final answer
   - `events.jsonl`: every step, including each tool call and result
   - `workspace/`: any files the agent wrote
   - `metrics.json`: timings, tokens, cost, tool calls
5. **Calculates cost:** token counts × the OpenRouter list prices in `config/bench.json`.
6. **Keeps runs clean:** Hermes runs in its own process group, so a timeout stops it and anything it started. Its error log goes to a file so a noisy run can never stall.
7. **On the laptop only**, it also measures:
   - chip power (CPU + GPU + neural engine) with macOS `powermetrics`
   - peak memory of the local model server
   - any network connection leaving the laptop, sampled every second with `lsof`

Runs go profile by profile, three rounds of T1 to T6 each. Phase 1 is 54 cloud runs. Phase 2 is 18 laptop runs, plus 6 more with Wi-Fi off.

## How I score

Every output is graded on the full deliverable: the agent's final reply plus any files it wrote (`deliverable.md` in each run folder). In testing, the 9B agent sometimes saved its emails as files instead of pasting them into the reply. Grading only the reply would have scored real work as missing.


| Step | Script | Method |
|---|---|---|
| 1 | `check.py` | Rule-based, no AI: word counts, Q5 declined, caveats kept, T6 cells correct against the answer key, planted gaps marked |
| 2 | `judge.py` | GPT-6 Sol scores each output 1–5 on five criteria (facts, completeness, fit for the reader, ready to ship, format). It receives the task, the sources and the answer key, never the profile or model name. Outputs are shuffled, and each is graded three times at temperature 0; scores are averaged |
| 3 | Me | I re-grade T4 and T6 blind: each output is copied to `results/regrade/<id>.md` with the profile hidden, and I score it in `results/human_regrade.csv`; the report shows how often the judge and I agree within 2 points. Then I check every invented-fact flag the judge raised on those outputs against the sources (`results/judge_flag_audit.csv`, scored by `scripts/flag_audit.py`) |
| 4 | `report.py` | Builds the CSVs behind the results tables |

Hard gates keep a fluent but wrong answer from scoring well. An invented fact found by any judge pass caps the facts score at 2 and makes the output unusable. So does repeating the T2 rumor's price cut. A missing T6 file caps completeness at 2. A fabricated answer to T4 Q5 fails the trust test outright. An output counts as **usable** only at 20/25 or higher with no gate triggered.

## Where the numbers are approximate

I want these limits to be visible, not discovered:

- **Cost** is tokens × list price, with cache discounts ignored, so cloud cost is slightly overstated.
- **Time to first output** is when the model first produces text or a tool call, measured from the start of the Hermes session. It includes prompt processing, which dominates on the laptop.
- **Tokens per second** is output tokens ÷ total task time. It measures end-to-end throughput, not raw generation speed.
- **Energy** covers the chip, not the display, and only on the laptop. Cloud energy cannot be measured from outside, so I make no comparative energy claim.
- **The judge is an AI.** I mitigate that with a different model family, blind grading and three passes, and I checked it: all 38 of its fact flags on T4 and T6 held up, though my blind totals matched it within 2 points on only 38% of those outputs. Claims are published only where the judge and I agree.
- **Hosted vs local precision:** pmm-a runs at the provider's precision and pmm-d at 8-bit. Measuring that gap is part of Phase 2.
- **The frontier model thinks adaptively.** Claude Sonnet 5.5 decides for itself when to reason, and OpenRouter does not fully switch that off. With reasoning set to none it still produced several thousand hidden reasoning tokens on long tasks (about 850 visible tokens vs about 7,900 billed on T1). Those tokens are billed, so they are in its cost. The open models ran with thinking off. I kept this as is: the frontier baseline represents cloud quality as customers actually get it.
- **The laptop is a floor.** A fanless consumer laptop is not a workstation. More memory and active cooling raise the ceiling.
- **Three runs per task** show a pattern, not a statistical rate.

## Design decisions and why

- **Reasoning off everywhere.** Every model gets the same setting, so the comparison is about the model rather than how long it thinks. Extended thinking would also be very slow on a fanless laptop. A reasoning-on run is a natural next experiment.
- **A cross-family judge.** No contestant is graded by its own model family.
- **Fictional inputs.** I control the facts, so every invented detail is detectable, and no real company data is involved.
- **One agentic task (T6).** T1 to T5 measure writing quality cleanly. T6 measures whether the model can act as an agent: plan, call tools, read and write files.

## Reproduce it

Follow the runbook in the [README](../README.md). In short:

```bash
export OPENROUTER_API_KEY=sk-or-...
./profiles/setup_profiles.sh                                    # create the four agents
python3 scripts/set_local_model.py                              # after downloading the local model
python3 scripts/run_bench.py --profiles pmm-a,pmm-b,pmm-c       # Phase 1
sudo -v && python3 scripts/run_bench.py --profiles pmm-d --energy --cooldown 10   # Phase 2
python3 scripts/check.py && python3 scripts/judge.py && python3 scripts/report.py # score
```
