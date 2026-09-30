# Blind Re-grade Guide (T4 and T6)

Purpose: check the AI judge. I grade 24 outputs myself, blind, on the same rubric. `report.py` then shows how often the judge and I agree (within 2 points of 25).

**Rules for staying blind**
- Grade only from `results/regrade/<id>.md`. Don't open `runs/`, `judge_pass*.json`, or `results/.regrade_map.json` until I'm done.
- Grade each output on its own merits. Don't try to guess which model wrote it.

**How**
1. Open `results/human_regrade.csv` in Numbers.
2. For each row, open the file named in the `file` column (Finder: `results/regrade/`).
3. Enter a whole number from 1 to 5 in each of the five columns: facts, complete, reader, ready, format. Add a short note if something stands out.
4. Save: File → Export To → CSV, same name and place (`results/human_regrade.csv`), replacing the original.
5. In Terminal, from the project folder: `python3 scripts/report.py`. It prints the agreement line.

About 20–30 minutes: T4 outputs are short, T6 outputs are one table plus three bullets.

---

## Rubric (same as the judge)

| Score | facts | complete | reader | ready | format |
|---|---|---|---|---|---|
| 5 | Every claim traceable to the source | Every part asked for is present | Tone and framing fit the reader | Send as is, or with trivial edits | Length, counts, structure exactly right |
| 4 | One trivial stretch | One minor part thin | Mostly fits | Light edits | One small slip |
| 3 | One unsupported claim | One part missing | Generic | Real edits needed | Noticeable deviation |
| 2 | Several unsupported claims (cap here if **any** fact is invented) | Several parts missing | Poor fit | Heavy rewrite | Several deviations |
| 1 | Mostly invented or wrong | Mostly missing | Wrong reader | Unusable | Ignores the format |

Invented fact = any spec, number, policy, name or claim not in the source. If you find one, facts is 2 at most.

---

## T4 answer key: Customer FAQ

The task: answer 5 questions using only the product docs, cite the section for each, and reply exactly "Not covered in the provided documentation" (plus who to contact) when the docs don't answer.

| Q | Correct answer | Section |
|---|---|---|
| Q1 Upgrade 32 GB → 128 GB myself? | Yes. Two SO-DIMM slots, up to 128 GB, customer may upgrade; warranty not voided with qualified modules from the compatibility list | 2 |
| Q2 Standard warranty, can I extend? | 3-year on-site, next-business-day; extendable to 4 or 5 years at purchase or within 90 days | 1 |
| Q3 Monitors from one dock? | Up to three external 4K 60 Hz displays through one Thunderbolt 5 dock (or two 8K 60 Hz); HDMI 2.1 adds one more at up to 4K 120 Hz | 3 |
| Q4 BIOS attacked? | Self-healing BIOS checks firmware integrity and restores a protected copy at the next boot | 4 |
| Q5 Ubuntu 24.04 certified? | **"Not covered in the provided documentation"** + suggest who to contact. Answering yes or no, or inferring from "Windows 11 Pro", is wrong | none |

Watch for: invented policies, SKUs, timelines or contact names; a missing section citation (hurts complete/format); a wrong Q5.

---

## T6 answer key: Competitive spec matrix

The task: a table of all three products across 8 attributes, "not stated" where the files don't say, then 3 Aurora 14 differentiators the table supports.

| Attribute | Aurora 14 | Vantage Pro 16 | Summit X15 |
|---|---|---|---|
| CPU | Helix H9 AI, 16 cores | Corvex X12, 14 cores | Helix H7 AI, 12 cores |
| GPU | Vireo V8000 Pro, 16 GB | Vireo V9000, 24 GB | Vireo V6000, 8 GB |
| Max memory | 128 GB (user-upgradeable) | 64 GB (soldered) | 96 GB |
| Max storage | 4 TB | 2 TB | **not stated** |
| Display | 14" OLED 2880×1800, 120 Hz | 16" IPS 2560×1600, 165 Hz | 15.6" OLED 3840×2400, 60 Hz |
| Weight | 1.65 kg | 2.30 kg | 1.95 kg |
| Battery | 86 Wh | 99 Wh | **not stated** |
| Ports | 2× TB5, USB-A, HDMI 2.1, SD reader | **not stated** | 2× TB4, USB-A, HDMI 2.1 |

Differentiators the table supports: most memory (128 GB, upgradeable), most storage (4 TB), lightest (1.65 kg), Thunderbolt 5.

Watch for: claims the table can't support ("fastest GPU", "best AI performance", "TB5 is faster" as a spec claim), anything filled in where the answer is "not stated", or claims about Vantage's ports or Summit's battery/storage.
