# Findings Log

*Joab Paiva · running record of results, observations and decisions, written as they happen.*

Status: **Phase 1 complete and graded (54 runs). Phase 2 (laptop) pending.** Numbers below are Phase 1 only and become final after Phase 2 grading.

---

## Phase 1 results (cloud, 30 Sep 2026)

18 runs per agent (6 tasks × 3 runs). Quality is the judge's score out of 25 (mean of 3 blind passes), median of 3 runs, spread in brackets.

| Task | pmm-a 9B hosted | pmm-b 27B hosted | pmm-c Frontier |
|---|---|---|---|
| T1 Launch blog | 16.3 (5.7) | 18.0 (0.0) | 20.0 (5.0) |
| T2 Battlecard | 16.7 (2.0) | 19.0 (0.7) | 21.0 (5.0) |
| T3 Exec summary | 13.3 (4.0) | 15.0 (6.7) | 13.7 (5.3) |
| T4 Customer FAQ | 23.3 (6.3) | 21.0 (4.0) | 24.3 (1.0) |
| T5 Email sequence | 9.7 (1.7) | 13.7 (3.3) | 18.0 (1.0) |
| T6 Spec matrix | 14.3 (5.0) | 19.7 (1.3) | 19.7 (1.3) |
| **Average** | **15.6** | **17.7** | **19.4** |
| % of frontier | 80% | 91% | 100% |
| Usable outputs | 2 of 18 | 1 of 18 | 7 of 18 |

| Metric | pmm-a | pmm-b | pmm-c |
|---|---|---|---|
| Cost per task | $0.0010 | $0.0024 | $0.0500 |
| Cost per usable output | $0.009 | $0.042 | $0.129 |
| Latency per task | 14.7 s | 10.7 s | 24.6 s |
| Time to first output | 4.7 s | 3.1 s | 19.9 s |
| Output tokens per second | 65 | 57 | 135 |
| Invented facts (total, 18 outputs) | 61.7 | 54.7 | 10.3 |
| T4 Q5 declined correctly | 3 of 3 | 3 of 3 | 3 of 3 |
| T6 cells correct | 24/24 | 24/24 | 24/24 |
| T6 gaps marked "not stated" | 3/3 | 3/3 | 3/3 |
| T6 tool calls succeeded | 91% | 100% | 100% |
| Score spread across runs (avg) | 4.1 | 2.7 | 3.1 |
| Total spend, 18 runs | $0.018 | $0.042 | $0.90 |

Judge spend for Phase 1: $1.38 (162 gradings).

## What the data says so far

1. **Invented claims are the real differentiator, not writing quality.** The open models average 3 invented claims per output; the frontier model about 0.6. Typical inventions are plausible marketing benefits the source never states: "reduces bandwidth costs", "protecting your investment", "eliminates waits for cloud sync", or dropping a qualifier ("runs 30B models" without "with 64 GB or more").
2. **Trust and agent mechanics are a tie.** Every model declined the unanswerable Q5 in all runs, and every model built the T6 table perfectly (24/24 cells, 3/3 gaps). The 9B model needed more tool calls and 2 of 22 failed; it recovered.
3. **Size helps, mostly on complex writing.** 27B vs 9B: +2.1 points on average, +5.4 on T6 and +4.0 on T5. On T4 the 9B scored slightly higher.
4. **The frontier model costs about 50× the 9B per task** ($0.050 vs $0.001), partly because it reasons adaptively even with reasoning off (about 850 visible vs about 7,900 billed tokens on T1).
5. **Usable outputs are rare everywhere** because the rule is strict: any invented fact makes an output unusable. Requiring 2 of 3 judge passes instead would change only two outputs, so the rule set before the runs stands.
6. **T3 is hard for all models** because the prompt asks for every test condition within 250 words; the judge docks all models for omitted test details. The six planted caveats were kept well by 27B (5.3/6) and frontier (5.7/6), less by 9B (4/6).
7. **The frontier model overshoots length:** all three T1 blogs were about 640 words against a 500–600 limit.
8. **One genuine 9B failure:** T5 run 1 stopped after writing its plan and "Email 1". Consistency is the 9B's weak spot (largest run-to-run spread).

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

## Open items

- Phase 2: 18 laptop runs with power measurement, then 6 runs with Wi-Fi off.
- Grade Phase 2; human re-grade of T4 and T6 (24 outputs) to measure judge agreement.
- Fill the deck's results, assessment and claims from the final CSVs.
