#!/usr/bin/env bash
# Headless version of the chain for scripts/CI (Lesson 3.9.3 note on `claude -p`).
# Each stage runs, then its output is validated against the contract. A failed stage
# is retried ONCE on its own - earlier stages are not re-run (intermediate outputs on disk).
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p pipeline

stage() { # name, prompt, output, schema(optional)
  local name=$1 prompt=$2 out=$3 schema=${4:-}
  for attempt in 1 2; do
    echo "== $name (attempt $attempt)"
    claude -p "$prompt" --permission-mode acceptEdits --allowedTools "Read,Write,Agent" < /dev/null \
      | tail -n 3
    if [[ -n "$schema" ]]; then
      python3 tools/validate_contract.py "$out" "$schema" && return 0
    else
      [[ -s "$out" ]] && return 0
    fi
    echo "   $name output invalid - retrying stage $name only"
  done
  echo "!! $name failed twice - stopping pipeline"; exit 1
}

if [[ ! -s pipeline/stage1-issues.json ]] || [[ "${FORCE:-}" == 1 ]]; then
  stage extract "Use the ticket-extractor subagent on input/support-tickets.txt." \
        pipeline/stage1-issues.json contracts/stage1-issues.schema.json
else
  echo "== extract: output exists, skipping (FORCE=1 to redo)"
fi
stage triage "Use the issue-triager subagent." pipeline/stage2-triage.json contracts/stage2-triage.schema.json
stage report "Use the report-writer subagent." pipeline/stage3-report.md
echo "== done: pipeline/stage3-report.md"
