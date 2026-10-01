# Findings Log

*Joab Paiva · running record of results, observations and decisions, written as they happen.*

Status: **Complete.** 72 measured runs judged and rule-checked; 6 Wi-Fi-off runs rule-checked; blind human re-grade and judge fact-flag audit done.

---

## Final results

Quality is the judge's score out of 25 (mean of 3 blind passes), median of 3 runs, spread in brackets.

| Task | pmm-a 9B hosted | pmm-b 27B hosted | pmm-c Frontier | pmm-d 9B on laptop |
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

| Metric | pmm-a | pmm-b | pmm-c | pmm-d |
|---|---|---|---|---|
| Cost per task | $0.0010 | $0.0024 | $0.0500 | $0.000045 (electricity) |
| Cost per usable output | $0.009 | $0.042 | $0.129 | $0.0004 |
| Latency per task | 14.7 s | 10.7 s | 24.6 s | 72.2 s |
| Time to first output | 4.7 s | 3.1 s | 19.9 s | 7.9 s |
| Output tokens per second | 65 | 57 | 135 | 8.1 |
| Invented claims (hallucinations), total of 18 outputs | 61.7 | 54.7 | 10.3 | 52.7 |
| T4 Q5 declined correctly | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| T6 cells / gaps | 24/24, 3/3 | 24/24, 3/3 | 24/24, 3/3 | 24/24, 3/3 |
| T6 tool calls succeeded | 91% | 100% | 100% | 100% |
| Score spread across runs (avg) | 4.1 | 2.7 | 3.1 | 5.8 |
| Energy per task (chip only) | n/a | n/a | n/a | 0.11 Wh (0.04–0.28) |
| Peak model memory | n/a | n/a | n/a | 11.9 GB of 24 |
| Connections off-device | all task data | all task data | all task data | none in 18 runs |
| Works with Wi-Fi off | no | no | no | 6 of 6 tasks completed |

**Electricity rate:** $0.403/kWh, the blended energy charge (PG&E delivery + Pioneer Community Energy generation, net of the generation credit, excluding the fixed daily base charge) from my Jul 27–Aug 25 2026 bill on the E-ELEC time-of-use rate. Peak-hour all-in is about $0.63/kWh, which would put laptop cost at about $0.00007 per task. Energy is chip only (CPU + GPU + neural engine), not the display or the rest of the laptop.

**Spend:** Phase 1 agents $0.96; judge $1.79 (216 gradings) plus $0.30 of smoke-test grading; laptop runs about $0.0008 in electricity.

**Machine:** MacBook Air (Mac15,12), Apple M3, 8-core CPU (4P + 4E), 10-core GPU, 24 GB unified memory, fanless; macOS 27.0.1; Hermes Agent v0.21.5; llama.cpp build 10964 (Metal) serving Qwen3.5-9B Q8_0 (9.5 GB), 64K context, thinking off, localhost only. Plugged in.

## What the data says

1. **Moving the 9B model onto the laptop did not cost quality.** Laptop 17.0 vs hosted twin 15.6. The difference is within run-to-run spread, so the fair reading is "no quality loss on-device", not "local is better". Possible contributors: 8-bit local weights vs the hosted provider's precision and runtime.
2. **The laptop model is within 10% of the frontier on the FAQ and the executive summary, and within 15% on the spec matrix** (both graders agree on T4 and T6; T3 is judge-only). Judge scores: T3 15.0 vs 13.7 (109%), T4 23.3 vs 24.3 (96%), T6 19.0 vs 19.7 (96%); my blind re-grade puts T6 at 86%. T2 is just outside (89%). Overall 87% of frontier.
3. **Where the cloud wins: grounded persuasive writing.** The frontier model made about 0.6 invented claims per output vs about 3 for every open model, hosted or local. It led most on the launch blog (20.0 vs 13.3) and the email sequence (18.0 vs 12.7). It was also about 17× faster at generating text than the laptop (135 vs 8 tokens/sec; the hosted 9B was about 8× faster) and more consistent (spread 3.1 vs 5.8).
4. **Trust and agent mechanics are close to a tie across all four.** Every configuration declined the unanswerable Q5 in every run and built the T6 table perfectly (24/24 cells, 3/3 gaps). The laptop had zero tool errors; the hosted 9B had 2 of 22. Nuance: 4 of 9 open-model Q5 declines (1 of 3 on the laptop) added an unsupported referral; the frontier's never did.
5. **Cost:** laptop about $0.000045 per task in electricity, about 22× cheaper than the hosted 9B and about 1,100× cheaper than the frontier ($0.050). Hardware is excluded and shown separately.
6. **Privacy:** no connection left the laptop in any of the 18 measured runs, and all 6 tasks completed with Wi-Fi off.
7. **Size helps:** 27B vs 9B +2.1 points, closing 55% of the 9B-to-frontier gap; biggest on T6 (+5.4) and T5 (+4.0). (Judge scores; my blind re-grade shows no T6 lift.)
8. **Speed on a fanless laptop:** about 5× slower end to end (72 vs 15 s per task). Generation speed 8.3 tokens/sec in the first four runs vs 7.7 in the last four; round averages 8.1, 8.3 and 7.9 across the 25-minute run. Chip power fell from about 8 W in round 1 to about 4.4 W afterwards with no change in speed; reported as observed, cause not determined.
9. **The 9B's weak spot is consistency.** Both the hosted and the laptop 9B wrote only part of the T5 sequence once (the hosted run stopped after its plan and "Email 1"; the laptop run wrote one email of three). Largest run-to-run spread of all configurations.
10. **The frontier model thinks even with reasoning off.** Claude Sonnet 5.5 reasons adaptively and OpenRouter does not fully switch that off: about 850 visible vs about 7,900 billed tokens on T1. The open models ran with thinking off. Kept and disclosed: the frontier baseline represents cloud quality as customers actually get it.
11. **T3 is hard for all models** because the prompt asks for every test condition within 250 words; the judge docks every model for omitted test details, equally.
12. **Usable outputs are rare everywhere** because one invented claim makes an output unusable. Requiring 2 of 3 judge passes instead would lift the gate on only two outputs (both T3, below 20), so no usable count changes; the flag audit later confirmed all 9 single- or double-pass flags were real.
13. **Offline T6 took 259 s** because the agent took a longer path (wrote the file before reading the inputs, then rewrote it: 7 tool calls vs 5); still 24/24.

## Marketing claims (final)

| # | Marketing claim | Built on | Bar status |
|---|---|---|---|
| 1 | Your work never leaves your machine | Bar B (connections) | Met |
| 2 | AI that works where Wi-Fi doesn't | Bar B (offline) | Met |
| 3 | Near-cloud quality on work grounded in your own documents | Bars A and E | Narrowed: 2 tasks within 10%, 1 within 15%; declines to guess met |
| 4 | No meter running | Bar C | Met |
| 5 | More memory, better AI | Bar D | Judge-measured; not reproduced on T6 by hand |

Proof points come from a fanless consumer laptop (the floor); re-run on the target HP workstation before market.

## Proof bars (set before the runs)

Publishing rule: quality claims use the median of 3 runs; behavior claims must hold in all 3 runs; where both grades exist, judge and human must agree.

| # | Claim | Bar | Result |
|---|---|---|---|
| A | Laptop model within 10% of frontier on everyday tasks | Within 10% on 3+ tasks | **Partly met:** T3 and T4 within 10%; T6 within 15% (judge 96%, my re-grade 86%) |
| B | No task data leaves the laptop; works offline | No outside connections; offline completes | **Met:** none in 18 runs; 6/6 offline |
| C | On-device cost per task vs cloud | Measured on all runs | **Met:** $0.000045 vs $0.0010 / $0.050 |
| D | Workstation-class memory (27B) lifts quality | Gain of 2+ points | **Met per judge (+2.1, closes 55% of the gap); my T6 re-grade shows no lift, so stated as judge-measured** |
| E | Laptop model declines to guess | 3 of 3 runs | **Met:** 3 of 3 (one decline added an unsupported referral) |

Decision: apply the rule as written, so bars A and D are narrowed; they carry into marketing claims 3 and 5.

## What the validation caught before the real runs

| Found in | Problem | Fix |
|---|---|---|
| Smoke test | Hermes tells the model its project folder; the folder name ("hp-pmm-…") leaked into answers as an invented "HP" contact, and one model looked for files in the wrong folder | Agents run in a neutral scratch folder outside the repo; repo renamed |
| Smoke test | `hermes config set agent.reasoning_effort none` stored an empty value, which means "provider default" (thinking on) | Write the string "none" directly |
| Local setup | pmm-d inherited a cloud (Anthropic) address from the default profile | Removed; setup now clears it; the connection monitor caught it |
| Local setup | Hermes refuses local models below a 64K context window | Local server pinned at 64K |
| Independent code review | Power readings stalled after seconds; stderr could deadlock a run; timeouts didn't kill child processes | Fixed and re-tested with fault injection |
| Live end-to-end test | The 9B saved T5 emails as files instead of replying; grading only the reply scored real work 6/25 | Grade the full deliverable (reply + files written); same output scored 16.5 |
| Live end-to-end test | Scoring rules misfired on markdown bold, subject-line variants, extra table rows | Checks rewritten and tested on realistic samples |
| Judge review | Judge scores moved between grading sessions | 3 passes per output instead of 2 |

## Judge fact-flag audit (human, not blind)

- I checked every invented-claim flag the judge raised on the 24 re-graded outputs (38 distinct claims across 16 outputs) against the source facts: **38 of 38 real**, 0 borderline, 0 wrong.
- Flags found by only 1 or 2 of the 3 judge passes were as reliable as those found by all 3 (9/9 vs 29/29), so the "any pass" gate rule stands. No output changes usable status.
- Why my blind facts scores were high: I hadn't studied the source files, so unsupported comparisons read as plausible. That is how fabrications slip through a busy marketing review, and it's the case for automated fact-checking against sources.
- Even with the confirmed fact cap applied to my blind scores, agreement on totals stays at 9/24: I penalized the same flaws again under ready/reader/format (I'm then 2.4 points stricter than the judge).
- T6 with confirmed facts applied: laptop 18 vs frontier 21 (86%), judge 96%. 27B 11 vs hosted 9B 11 (no lift); judge +5.4.
- My T4/T6 re-grade used the frontier's saved T6 table only; the judge also saw its replies, which added commentary, and docked format for it.

## Open items

- Demo video.
