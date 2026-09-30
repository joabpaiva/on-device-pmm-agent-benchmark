#!/usr/bin/env python3
"""Point the pmm-d profile at the local server started by scripts/start_local_server.sh.

Run with the server already running in another Terminal window.
Usage: python3 scripts/set_local_model.py [port]
"""
import json, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
port = sys.argv[1] if len(sys.argv) > 1 else "8081"
base = f"http://127.0.0.1:{port}/v1"
try:
    models = [m["id"] for m in json.load(urllib.request.urlopen(base + "/models", timeout=10)).get("data", [])]
except Exception as e:
    sys.exit(f"Local server not reachable at {base} ({e}). Start it first: ./scripts/start_local_server.sh")
if not models:
    sys.exit("Server is up but reports no model.")
model = models[0]
print(f"Local server at {base} serves: {model}")

for key, val in [("model.provider", "llamacpp"),
                 ("providers.llamacpp.base_url", base),
                 ("providers.llamacpp.model", model),
                 ("model.default", model),
                 ("local_runtime.enabled", "false")]:   # use our server, not a second app-managed one
    subprocess.run(["hermes", "-p", "pmm-d", "config", "set", key, val, "--force"], check=True,
                   stdout=subprocess.DEVNULL)

# Remove any cloud endpoint inherited from the default profile, so pmm-d can only reach the local server
for key in ("model.base_url", "model.api_mode"):
    subprocess.run(["hermes", "-p", "pmm-d", "config", "unset", key], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

cfg_path = ROOT / "config/bench.json"
cfg = json.loads(cfg_path.read_text())
cfg["profiles"]["pmm-d"]["model"] = model
cfg_path.write_text(json.dumps(cfg, indent=2) + "\n")
print(f"pmm-d now uses {model} via {base}")
