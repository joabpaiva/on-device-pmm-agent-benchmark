#!/usr/bin/env bash
# Starts the local model server for pmm-d with fixed, documented settings.
#
# Uses the llama.cpp build that Hermes installed (same engine as Hermes' Local Models),
# but launches it explicitly so every setting is recorded and repeatable:
#   - Qwen3.5-9B, Q8_0 GGUF, fully on the Apple GPU (Metal)
#   - 64K context window, one request at a time (Hermes requires at least 64K)
#   - thinking off (--reasoning-budget 0), matching reasoning effort "none" on the hosted profiles
#   - listens on 127.0.0.1 only, so nothing outside this Mac can reach it
#
# Leave this Terminal window open while pmm-d runs. Ctrl-C stops the server.
set -euo pipefail

BIN=$(ls -d "$HOME"/.hermes/tools/llamacpp-metal-*/llama-server 2>/dev/null | tail -1)
MODEL="$HOME/.hermes/models/Qwen3.5-9B-Q8_0.gguf"
PORT="${PORT:-8081}"
ALIAS="qwen3.5-9b-q8_0"

[[ -x "$BIN" ]]   || { echo "llama-server not found under ~/.hermes/tools. Install the runtime in Hermes > Local Models." >&2; exit 1; }
[[ -f "$MODEL" ]] || { echo "Model not found: $MODEL" >&2; exit 1; }

echo "Engine: $("$BIN" --version 2>&1 | head -1)"
echo "Model:  $MODEL"
echo "Serving $ALIAS on http://127.0.0.1:$PORT/v1"
exec "$BIN" -m "$MODEL" --alias "$ALIAS" --host 127.0.0.1 --port "$PORT" \
  --ctx-size 65536 --parallel 1 --n-gpu-layers 99 --flash-attn auto --jinja --reasoning-budget 0
