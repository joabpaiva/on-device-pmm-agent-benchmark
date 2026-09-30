# Can a Laptop Do Product Marketing?

Benchmark of a Hermes Agent (Nous Research) product-marketing agent on open-weight models that can run on a laptop versus a frontier cloud model, then run on-device on a real laptop.

- **Phase 1 (cloud):** 6 PMM tasks × 3 runs on Qwen3.5-9B, Qwen3.5-27B (hosted via OpenRouter) and Claude Sonnet 5.5.
- **Phase 2 (on-device):** the same tasks on Qwen3.5-9B (8-bit) running locally through Hermes' built-in llama.cpp runtime.
- **Scoring:** scripted checks + a blind judge from a different model family (GPT-6 Sol) + a human re-grade of T4 and T6.

All products in the task inputs (Aurora 14, Vantage Pro 16, Summit X15) are fictional.

## Repo layout

```
tasks/        tasks.json (frozen prompts), inputs/ (source material), answer_keys.json
profiles/     SOUL.md (identical for all four agents), setup_profiles.sh
config/       bench.json: profiles, models, prices, judge, runs per task
scripts/      run_bench.py, check.py, judge.py, report.py, set_local_model.py
runs/         raw outputs, event logs and metrics for every run (created by run_bench.py)
results/      CSVs behind every results slide (created by report.py)
```

## Runbook

Everything below runs in Terminal on the Mac, from this folder. Scripts use only the Python standard library.

### 1. OpenRouter key
Create a key at openrouter.ai and add a few dollars of credit. The whole benchmark, judge included, should cost under $5.

```bash
export OPENROUTER_API_KEY=sk-or-...
```

### 2. Create the four profiles
```bash
chmod +x profiles/setup_profiles.sh
./profiles/setup_profiles.sh
```
Creates `pmm-a` … `pmm-d` with the same SOUL.md, memory off, background review off, reasoning effort `none`, and file tools only. Only the model differs.

### 3. Download the local model (Hermes desktop app)
1. Hermes → Settings → Providers → Local Models. Install the runtime if asked.
2. **Find more models** → search `unsloth/Qwen3.5-9B-GGUF` → download the **Q8_0** file (9.5 GB).
3. Load it, keep the Hermes app open (the local server runs with the app), then:
```bash
python3 scripts/set_local_model.py
```

### 4. Smoke test (2 runs, about 2 minutes)
```bash
python3 scripts/run_bench.py --profiles pmm-a,pmm-d --tasks T4 --runs 1 --label smoke
cat runs/smoke/pmm-a/T4/r1/response.md
```
Both should print `OK`. If a run fails, `runs/smoke/<profile>/T4/r1/stderr.txt` says why.

### 5. Phase 1: cloud (54 runs)
```bash
python3 scripts/run_bench.py --profiles pmm-a,pmm-b,pmm-c
```

### 6. Phase 2: on-device (18 runs)
Plug in, quit other heavy apps, keep the Hermes app open.
```bash
sudo -v                                   # lets the script read power via powermetrics
python3 scripts/run_bench.py --profiles pmm-d --energy --cooldown 10
```
Record the machine for the specs slide:
```bash
{ sw_vers; system_profiler SPHardwareDataType SPDisplaysDataType | grep -E "Model Name|Chip|Total Number of Cores|Memory|Chipset Model"; hermes --version; } > results/machine.md
```

### 7. Offline proof (6 runs)
Turn Wi-Fi off (screen-record this for the demo video), then:
```bash
python3 scripts/run_bench.py --profiles pmm-d --label offline --runs 1
```
Turn Wi-Fi back on afterwards.

### 8. Score and report
```bash
python3 scripts/check.py                  # scripted checks
python3 scripts/judge.py                  # blind judge, 2 passes per output (needs Wi-Fi)
python3 scripts/check.py --label offline
python3 scripts/report.py                 # writes results/*.csv and prints the tables
```
Optional: set `electricity_usd_per_kwh` in `config/bench.json` from your utility bill so pmm-d cost = measured Wh × your rate.

### 9. Human re-grade
Open `results/human_regrade.csv`, grade each T4 and T6 output 1–5 on the five criteria (find each output via `results/.regrade_map.json`, which is only for you), then rerun `python3 scripts/report.py`. It prints how often you and the judge agree within 2 points.

## What each metric means

| Metric | Source |
|---|---|
| Quality (of 25) | Judge, 5 criteria × 1–5, mean of 2 passes; median of 3 runs reported |
| Usable output | 20/25 or higher and no gate triggered (invented fact, unverified rumor, T6 file not saved, T4 Q5 fabricated) |
| Cost per task | Hermes token counts × OpenRouter list price in `config/bench.json` |
| Latency, time to first token, tokens/sec | Hermes `--format stream-json` timestamps |
| Tool calls / errors | stream-json `tool_use` and `tool_result` events |
| Energy per task | `powermetrics` combined CPU+GPU+ANE power × wall time (on-device only) |
| Peak model memory | resident memory of the llama-server process |
| Off-device connections | `lsof` sampling of the agent and model processes during every on-device run |

## Limitations
Fictional inputs; 3 runs per task; AI judge (blind, cross-family, human-checked); list prices on run day; hosted precision vs 8-bit local; a fanless consumer laptop is a floor, not a workstation result; prompts frozen with no retries.
