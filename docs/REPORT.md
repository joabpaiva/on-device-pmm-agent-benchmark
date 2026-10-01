# Can a Laptop Do Product Marketing?

**Benchmark report: a Hermes product-marketing agent on local open-weight models vs a frontier cloud model**

*Joab Paiva · September 2026 · Repo: github.com/joabpaiva/on-device-pmm-agent-benchmark*

---

## Summary

I built one product marketing agent in Hermes Agent (Nous Research) and ran the same six PMM tasks, three times each, on four configurations:

- Qwen3.5-9B, hosted
- Qwen3.5-27B, hosted
- Claude Sonnet 5.5 (frontier cloud)
- Qwen3.5-9B running on my own fanless MacBook Air

A blind judge from a different model family graded every output. Rule-based checks back it up, and I checked the judge myself: a blind re-grade of two tasks, then an audit of every claim it called invented (38 of 38 confirmed).

**What I found**

- **Moving the 9B model from the cloud onto the laptop cost no measurable quality:** 17.0 vs 15.6 out of 25, within run-to-run spread.
- **The laptop is close to the frontier on grounded work.** It came within 10% of the frontier on the customer FAQ and the executive summary, and within 15% on the competitive spec matrix; 87% of frontier quality overall.
- **The laptop cost about $0.00005 per task in electricity,** vs $0.001 hosted and $0.05 on the frontier model.
- **Nothing left the device.** No connection left the laptop in 18 measured runs, and all six tasks completed with Wi-Fi off.
- **Trust held everywhere.** Every configuration declined to answer a question its sources couldn't support, in every run.
- **The cloud's clear win is fewer invented claims:** 5× fewer than any open model, hosted or local. It was also much faster and more consistent.

**When should you run AI on your PC?** For everyday work grounded in your own documents: answering from product docs, summarizing reports, building comparison tables. Use the cloud for customer-facing persuasive copy, where invented claims are costly. The winning setup is hybrid: local by default, cloud and a human check before anything ships.

---

## 1. Task design and why

I wrote six tasks that a product marketer does every week, ordered from simplest to hardest. Each one isolates a different capability. All inputs are fictional products I created (Aurora 14, Vantage Pro 16, Summit X15), so every invented detail is detectable and no real company data is involved. Several tasks contain deliberate traps.

| Task | PMM job | What it tests | Trap |
|---|---|---|---|
| T1 Launch blog | Spec sheet → 500–600-word blog for IT buyers | Grounded long-form writing | Any spec, price or benchmark not in the sheet counts as invented |
| T2 Battlecard | Competitive one-pager, 350 words max | Fair comparison, persuasion without fabrication | The brief contains an unverified 10% price-cut rumor marked do-not-use |
| T3 Exec summary | 1,100-word white paper → 250 words + 3 key messages | Compression that keeps the fine print | Six caveats buried in the paper must survive |
| T4 Customer FAQ | Answer 5 questions from product docs, citing sections | Grounded answers; knowing when not to answer | Q5 (Ubuntu certification) has no answer in the docs |
| T5 Email sequence | 3 nurture emails, 120 words each, one CTA each | Many constraints at once | Word limits, one ask per email, no invented statistics |
| T6 Spec matrix | Read 3 files in different formats, build and save a comparison table | Tool use and multi-step agent work | 3 values deliberately missing; must be marked "not stated" |

The prompts are frozen in `tasks/tasks.json`; sources are in `tasks/inputs/`; answer keys are in `tasks/answer_keys.json`.

## 2. Setup

**The four agents.** There is one agent, cloned into four Hermes profiles that differ only in the model.

| Profile | Model | Runs on | What it answers |
|---|---|---|---|
| pmm-a | Qwen3.5-9B | OpenRouter (hosted) | What can a laptop-sized model do? |
| pmm-b | Qwen3.5-27B | OpenRouter (hosted) | What does workstation-class memory buy? |
| pmm-c | Claude Sonnet 5.5 | OpenRouter (cloud) | What is the best available quality? |
| pmm-d | Qwen3.5-9B, Q8_0 | My MacBook Air, llama.cpp | What changes on a real device? |

- **pmm-a vs pmm-b:** same model generation, so the only variable is size.
- **pmm-d vs pmm-a:** same model, so this isolates the on-device effect.
- **What all four share:** an identical SOUL.md, memory off, background review off, reasoning effort "none", file tools only, a fresh session per run, and a clean, neutral scratch folder.

**Test machine.**
- **Laptop:** MacBook Air (Mac15,12). Apple M3, 8-core CPU (4 performance + 4 efficiency), 10-core GPU, 24 GB unified memory, fanless. macOS 27.0.1. Plugged in for all measured runs.
- **Agent and runtime:** Hermes Agent v0.21.5. The local model ran on the llama.cpp build Hermes installed (build 10964, Metal backend), launched with pinned settings: Qwen3.5-9B Q8_0 (9.5 GB), fully on the GPU, 64K context (the minimum Hermes accepts), thinking off, reachable only from the Mac itself.

**How a run works.** A Python script calls the same Hermes profiles through Hermes's own command line:

```
hermes -p <profile> chat --query-file query.txt --format stream-json -t file --source tool --yolo --max-turns 30
```

Hermes streams each step as data: start, tool calls, first output, final answer, token counts and duration. The script saves the exact prompt, the reply, any files the agent wrote, the event log and the metrics for every run. On the laptop it also records:
- chip power (`powermetrics`)
- peak model memory
- every network connection leaving the machine, sampled each second

The runs: 6 tasks × 3 runs × 4 configurations = 72 measured runs, plus 6 more on the laptop with Wi-Fi off.

## 3. Evaluation method

**Three layers of grading.**
1. **Rule checks (no AI):** word and item counts, whether Q5 was declined, caveats kept, T6 cells against the answer key, and whether the T2 rumor was repeated.
2. **AI judge:** GPT-6 Sol, from a different company than every contestant. It receives the rubric, the task, the sources, the answer-key notes and the agent's full output (reply plus any files written). It never sees which agent wrote the output. Outputs are shuffled, and each is graded three times at temperature 0; scores are averaged.
3. **Human check:** I re-graded all T4 and T6 outputs blind, on the same rubric, then checked every invented-fact flag the judge raised on them against the sources. Results are in section 4.

**Rubric.** Five criteria scored 1–5 each (25 max): facts, completeness, fit for the reader, ready to ship, and format.

**Hard gates.** An invented fact found by any judge pass caps facts at 2 and makes the output unusable. So does repeating the T2 rumor. A missing T6 file caps completeness at 2. A fabricated Q5 answer fails the trust test.

**Usable output:** 20/25 or higher and no gate triggered.

**Other metrics:**
- Cost: Hermes token counts × OpenRouter list price. For the laptop, measured energy × my electricity rate.
- Latency, time to first output, tokens per second.
- Tool-call success, run-to-run spread.
- On the laptop: energy, peak memory, connections off-device.

**Validation before the measured runs.** Smoke tests, an independent code review and a live end-to-end test caught eight problems, all fixed before the real runs:
- Hermes leaked the project folder name into answers.
- A "reasoning off" setting silently stayed on.
- The laptop agent inherited a cloud address.
- Power readings stalled mid-run.
- A noisy run could hang.
- Grading missed work an agent saved as files.
- Rule checks misfired on formatting.
- Judge scores varied between grading sessions.

The full list is in `docs/FINDINGS.md`.

## 4. Results

Quality is the median of 3 runs out of 25, with the spread across runs in brackets.

| Task | 9B hosted | 27B hosted | Frontier | 9B laptop |
|---|---|---|---|---|
| T1 Launch blog | 16.3 (5.7) | 18.0 (0.0) | 20.0 (5.0) | 13.3 (3.7) |
| T2 Battlecard | 16.7 (2.0) | 19.0 (0.7) | 21.0 (5.0) | 18.7 (4.7) |
| T3 Exec summary | 13.3 (4.0) | 15.0 (6.7) | 13.7 (5.3) | 15.0 (4.3) |
| T4 Customer FAQ | 23.3 (6.3) | 21.0 (4.0) | 24.3 (1.0) | 23.3 (8.7) |
| T5 Email sequence | 9.7 (1.7) | 13.7 (3.3) | 18.0 (1.0) | 12.7 (8.0) |
| T6 Spec matrix | 14.3 (5.0) | 19.7 (1.3) | 19.7 (1.3) | 19.0 (5.3) |
| **Average** | **15.6** | **17.7** | **19.4** | **17.0** |
| % of frontier | 80% | 91% | 100% | 87% |
| Usable outputs | 2 of 18 | 1 of 18 | 7 of 18 | 2 of 18 |

| Metric | 9B hosted | 27B hosted | Frontier | 9B laptop |
|---|---|---|---|---|
| Cost per task | $0.0010 | $0.0024 | $0.0500 | $0.000045 |
| Latency per task | 14.7 s | 10.7 s | 24.6 s | 72.2 s |
| Output tokens per second | 65 | 57 | 135 | 8.1 |
| Invented claims per output | 3.4 | 3.0 | 0.6 | 2.9 |
| Q5 declined correctly | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| T6 cells / gaps correct | 24/24, 3/3 | 24/24, 3/3 | 24/24, 3/3 | 24/24, 3/3 |
| T6 tool calls succeeded | 91% | 100% | 100% | 100% |
| Run-to-run spread (avg) | 4.1 | 2.7 | 3.1 | 5.8 |

**Reading the results**
- **Invented claims are the real differentiator, not writing quality.** Open models average about 3 per output; the frontier about 0.6. Typical inventions are plausible benefits the source never states, such as "reduces bandwidth costs" or "protects your investment". Another common one is dropping a qualifier: "runs 30B models" without "with 64 GB or more".
- **Trust and agent mechanics are a tie.** Every configuration declined Q5 in every run and built the T6 table perfectly.
- **Size helps, per the judge.** 27B vs 9B adds 2.1 points and closes 55% of the gap to the frontier, with the biggest gains on T6 (+5.4) and T5 (+4.0). My blind re-grade did not reproduce the T6 gain, so I state this as judge-measured.
- **Usable outputs are rare everywhere** because one invented fact disqualifies an output. A looser rule (2 of 3 judge passes must flag) would change only two outputs, so the rule set before the runs stands.
- **T3 is hard for every model.** The prompt asks for every test condition within 250 words, and the judge docks all models equally for omitted test details.
- **The 9B's weak spot is consistency.** Both 9B versions once wrote only part of the T5 sequence.

### Checking the judge

I re-graded the two tasks with answer keys (T4 and T6, 24 outputs) blind, then checked every claim the judge called invented on those outputs against the source facts.

| Check | Result |
|---|---|
| Blind re-grade, totals | 9 of 24 outputs (38%) within 2 points of 25; mean gap 3.3 |
| Who is stricter? | Me, by 0.7 points on average: the judge is not lenient |
| Same best and worst? | Yes: frontier best (22.8 me, 21.9 judge); hosted 9B worst (16.0, 18.7) |
| Judge's invented-fact flags | 38 of 38 confirmed real |
| Flags found by only 1–2 of 3 passes | 9 of 9 confirmed, so the "any pass" gate stands |
| Where we split | T6, laptop vs frontier: 86% by hand vs 96% judge. T6, 27B vs hosted 9B: no lift by hand vs +5.4 judge |

**What it means.** The judge's fact-checking held up completely. On my blind pass I read for tone and polish and did not check every comparison against the spec files, so lines like "fastest connectivity" (no file gives port speeds) looked plausible to me. That is how fabrications slip through a busy marketing review, and it is the case for automated fact checks before anything ships. Where we differed in judgment, on T6, I narrowed the claims (section 6).

Two smaller differences: on T6 I saw only the saved table, while the judge also saw each agent's reply and docked replies that added commentary; and the T6 answer key listed "most storage" as supported although Summit's storage is not stated (the judge applied the strict reading; the key is kept as used so the grading reproduces).

## 5. On-device reality check (Phase 2)

| Measure | 9B hosted | 9B laptop | Matches or differs |
|---|---|---|---|
| Average quality | 15.6 | 17.0 | **Matches:** within run-to-run spread; no loss on-device |
| Latency per task | 14.7 s | 72.2 s | Differs: about 5× slower end to end |
| Generation speed | 65 tok/s | 8.1 tok/s | Differs: fanless laptop GPU vs datacenter |
| Works with Wi-Fi off | no | 6 of 6 tasks completed | Differs: needs no internet |
| Connections off-device | all task data | none in 18 runs | Differs: model served only on the Mac |
| Energy per task | not measurable | 0.11 Wh (0.04–0.28), chip only | |
| Peak model memory | n/a | 11.9 of 24 GB | Fits with room to spare |
| Speed over the hour | n/a | 8.3 → 7.7 tok/s (first vs last 4 runs); round averages all 8.1 | Small drift |
| Cost per task | $0.0010 | $0.000045 (electricity) | About 22× cheaper |

- **Where on-device matches Phase 1:**
  - quality
  - trust behavior: Q5 declined 3/3
  - agent mechanics: T6 perfect 3/3, with zero tool errors (the hosted 9B had 2)
- **Where it differs:** speed, which is the price of a fanless laptop, and privacy and cost, which favor the laptop.
- **Chip power** fell from about 8 W in the first round to about 4.4 W afterwards with no change in speed. I report this as observed; I did not determine the cause.
- **Earlier setup observation:** in the smoke test before the measured runs, Hermes itself made two startup metadata calls, a model catalog download and an update check. Neither carried task content.

## 6. Marketing output

### Proof-point claims

Each claim had a bar set before the runs, and a rule: a claim is published only where the judge and my re-grade agree. Three cleared the bar outright; two are narrowed.

1. **Close to the cloud on grounded work.** A 9B model on a fanless laptop scored within 10% of a frontier cloud model on answering customer FAQs and summarizing a technical paper, and within 15% on building a competitive spec matrix. *Data: quality scoreboard, 3 runs × 3 blind judge passes; my blind re-grade of T4 and T6. Bar (3 tasks within 10%): partly met. The judge had T6 at 96%; my re-grade at 86%.*
2. **Nothing leaves the device.** Across 18 on-device runs, no connection left the laptop, and all six tasks completed with Wi-Fi off. *Data: per-second connection log; Wi-Fi-off rerun.*
3. **A fraction of a cent.** On the laptop, a marketing task cost about $0.00005 in electricity, vs $0.001 on a hosted 9B model and $0.05 on a frontier cloud model. *Data: measured energy × $0.403/kWh; token counts × list price.*
4. **Memory buys quality, per the judge.** Stepping up from a 9B to a 27B model, the size that needs workstation-class memory, added 2.1 points in the judge's scores and closed 55% of the gap to the frontier. *Data: pmm-a vs pmm-b, same model generation (hosted proxy). My blind re-grade did not reproduce the gain on T6, so this is stated as judge-measured.*
5. **It knows what it doesn't know.** When the answer wasn't in the source, the laptop model declined to guess in 3 of 3 runs, the same as the frontier model. *Data: T4 Q5 outputs and rule check.*

### Where the cloud beats local, stated honestly

- **Fewer invented claims:** 0.6 per output vs 2.9 on the laptop, about 5× fewer. This matters most for anything customer-facing.
- **Persuasive, constrained copy:** launch blog 20.0 vs 13.3; email sequence 18.0 vs 12.7.
- **Speed:** 135 vs 8 tokens/sec; 25 vs 72 seconds per task.
- **Consistency:** run-to-run spread 3.1 vs 5.8.

Where I expected the cloud to win and it didn't: the agent mechanics on T6. All four configurations built the table perfectly. On the writing around the table, the judge saw a tie (19.7 vs 19.0) and my re-grade favored the cloud.

### When should you run AI on your PC?

Run AI on your PC for everyday work grounded in your own documents: answering from product docs, summarizing reports, building comparison tables. There, a 9B model on a fanless laptop came within 10% of a frontier cloud model on docs and summaries, and within 15% on tables, for about $0.00005 a task, with every prompt kept on the device. Use the cloud for customer-facing persuasive copy, where the frontier model made 5× fewer unsupported claims. The winning setup is hybrid: local by default, cloud and a human check before anything ships.

## 7. Limitations and caveats

- **Inputs:** fictional products written for this test, not real HP or competitor data.
- **Sample size:** 3 runs per task show a pattern, not a statistical rate.
- **Judge:** quality is graded by an AI, blind, cross-family, three passes per output. I confirmed all 38 of its fact flags on T4 and T6, but my blind totals matched it within 2 points on only 38% of those outputs.
- **Prices:** OpenRouter list prices on run day. OpenRouter may route a model to different providers.
- **Precision:** the hosted model runs at the provider's precision and the local one at 8-bit. The laptop-vs-hosted quality difference is within spread and is not a claim that local is better.
- **The laptop is a floor.** A fanless consumer laptop is not a workstation; more memory and active cooling raise the ceiling.
- **Energy:** chip only (CPU, GPU, neural engine), not the display. The electricity rate is the blended energy charge from one bill ($0.403/kWh; about $0.63 at peak hours). Hardware cost is excluded.
- **Frontier thinking:** the frontier model thinks adaptively even with reasoning set to none, about 850 visible vs 7,900 billed tokens on T1. The open models ran with thinking off. I kept this and disclose it, because it is cloud quality as customers actually get it.
- **No retries:** prompts are frozen with no retries, unlike real work.

## 8. Reproduce it

Everything is in the repo: prompts, inputs, answer keys, profiles, scripts, all 78 run folders and the CSVs behind every table. See `README.md` for the runbook and `docs/HOW_IT_WORKS.md` for the full method. Total spend: about $0.96 for the cloud agents, $2.09 for grading, and under a tenth of a cent of electricity for the laptop runs.
