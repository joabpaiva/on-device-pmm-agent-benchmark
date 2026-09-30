#!/usr/bin/env bash
# Creates the four benchmark profiles (pmm-a..pmm-d) with an identical SOUL.md and settings.
# Only the model and provider differ. Safe to re-run: existing profiles are reconfigured, not recreated.
#
# Usage:  OPENROUTER_API_KEY=sk-or-... ./profiles/setup_profiles.sh
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  echo "Set OPENROUTER_API_KEY first:  export OPENROUTER_API_KEY=sk-or-..." >&2
  exit 1
fi

DESC="Product Marketing Agent: turns specs, briefs and research into launch content, sales enablement and customer answers, grounded only in the material provided."
HERMES_HOME_ROOT="${HERMES_HOME_ROOT:-$HOME/.hermes}"

for p in pmm-a pmm-b pmm-c pmm-d; do
  if [[ ! -d "$HERMES_HOME_ROOT/profiles/$p" ]]; then
    echo "== creating $p"
    hermes profile create "$p" --no-skills --description "$DESC"
  else
    echo "== $p exists, reconfiguring"
  fi

  cp profiles/SOUL.md "$HERMES_HOME_ROOT/profiles/$p/SOUL.md"

  # Fairness settings, identical in every profile
  hermes -p "$p" config set memory.memory_enabled false
  hermes -p "$p" config set memory.user_profile_enabled false
  hermes -p "$p" config set auxiliary.background_review.enabled false
  # `config set` stores the word none as YAML null (= provider default), so write the string directly
  hermes -p "$p" config set agent.reasoning_effort low --force >/dev/null
  sed -i '' 's/^  reasoning_effort:.*$/  reasoning_effort: "none"/' "$HERMES_HOME_ROOT/profiles/$p/config.yaml"
  hermes -p "$p" config set terminal.cwd .   # file tools resolve from the run folder the script launches in
done

# Model per profile (read from config/bench.json)
for p in pmm-a pmm-b pmm-c; do
  model=$(python3 -c "import json;print(json.load(open('config/bench.json'))['profiles']['$p']['model'])")
  hermes -p "$p" config set model.provider openrouter
  hermes -p "$p" config set model.default "$model"
  hermes -p "$p" config set OPENROUTER_API_KEY "$OPENROUTER_API_KEY"
  echo "   $p -> openrouter / $model"
done

hermes -p pmm-d config set model.provider llamacpp
hermes -p pmm-d config set local_runtime.enabled true
echo "   pmm-d -> llamacpp (model set later by scripts/set_local_model.py)"

echo
echo "Done. Next: download the local model (README step 3), then run scripts/set_local_model.py"
