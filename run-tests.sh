#!/usr/bin/env bash
# Run every offline test in the workshop (no Claude, no network, stdlib Python only).
set -u
cd "$(dirname "$0")"
fail=0
run() { echo; echo "=== $1"; shift; ( "$@" ) || { echo "!!! FAILED"; fail=1; }; }

run "lint all agent definitions"      python3 tools/lint_agents.py --all
run "demo 06 restrict_writes hook"    bash module-3-advanced-patterns/demo-06-permission-modes/hooks/test_restrict_writes.sh
run "demo 07 state validator"         bash -c "cd module-3-advanced-patterns/demo-07-memory-and-state && python3 tools/validate_state.py && ! python3 tools/validate_state.py tests/fixtures/corrupted-state.md >/dev/null"
run "demo 08 style checker finds 10"  bash -c "cd module-3-advanced-patterns/demo-08-skills-preload && python3 .claude/skills/tidewater-python-style/scripts/check_style.py src/legacy_orders.py | grep -q '10 finding'"
run "demo 09 hooks"                   bash -c "cd module-3-advanced-patterns/demo-09-hooks-guard-and-audit && python3 setup_db.py >/dev/null && python3 -m unittest tests/test_hooks.py"
run "demo 11 contract validator"      bash -c "cd module-3-advanced-patterns/demo-11-chaining-pipeline && echo '[]' > /tmp/_s1.json && ! python3 tools/validate_contract.py /tmp/_s1.json contracts/stage1-issues.schema.json >/dev/null"
run "demo 14 task list tool"          bash -c "cd module-4-agent-teams/demo-14-hand-authored-tasklist && python3 -m unittest tests/test_tasklist.py"
run "demo 15 quality gates"           bash -c "cd module-4-agent-teams/demo-15-quality-gates && python3 -m unittest tests/test_gates.py"
run "demo 17 reproducer (serial)"     bash -c "cd module-4-agent-teams/demo-17-competing-hypotheses && python3 repro/concurrent_orders.py --serial --trials 3 | grep -q 'NEGATIVE stock : 3/3'"

echo
[[ $fail -eq 0 ]] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit $fail
