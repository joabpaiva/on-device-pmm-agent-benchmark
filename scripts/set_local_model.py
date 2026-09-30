#!/usr/bin/env python3
"""Find the model served by Hermes' local llama.cpp runtime and point pmm-d at it.

Run after downloading Qwen3.5-9B (Q8_0) in Hermes > Settings > Providers > Local Models,
with the Hermes desktop app open so the local server is running.

Usage: python3 scripts/set_local_model.py            # list served models, pick the Qwen3.5-9B one
       python3 scripts/set_local_model.py <model-id>  # set explicitly
"""
import json, os, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
server = Path.home() / ".hermes/runtimes/llamacpp/server.json"
if not server.exists():
    sys.exit(f"No local server state at {server}. Open the Hermes desktop app and start the local model.")
info = json.loads(server.read_text())
req = urllib.request.Request(info["base_url"].rstrip("/") + "/models",
                             headers={"Authorization": f"Bearer {info.get('api_key','')}"})
try:
    models = [m["id"] for m in json.load(urllib.request.urlopen(req, timeout=10)).get("data", [])]
except Exception as e:
    sys.exit(f"Local server not reachable at {info['base_url']} ({e}). Is the Hermes app open with the model loaded?")

print("Models served locally:")
for m in models:
    print("  ", m)

if len(sys.argv) > 1:
    choice = sys.argv[1]
else:
    cands = [m for m in models if "qwen3.5-9b" in m.lower().replace("_", "-")]
    if len(cands) != 1:
        sys.exit("Could not pick a single Qwen3.5-9B model automatically; pass the id as an argument.")
    choice = cands[0]

subprocess.run(["hermes", "-p", "pmm-d", "config", "set", "model.default", choice], check=True)
cfg_path = ROOT / "config/bench.json"
cfg = json.loads(cfg_path.read_text())
cfg["profiles"]["pmm-d"]["model"] = choice
cfg_path.write_text(json.dumps(cfg, indent=2))
print(f"pmm-d now uses {choice}. Record the quantization (should be Q8_0) in results/machine.md.")
