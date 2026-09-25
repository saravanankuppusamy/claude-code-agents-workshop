#!/usr/bin/env bash
# Pipe representative payloads into the hook - test BEFORE wiring it to an agent.
cd "$(dirname "$0")/.."
export CLAUDE_PROJECT_DIR="$PWD"
pass=0; fail=0
check() { # name, payload, expect(allow|deny)
  out=$(echo "$2" | python3 hooks/restrict_writes.py out); code=$?
  if [[ "$out" == *'"deny"'* ]]; then got=deny; else got=allow; fi
  if [[ $code -eq 0 && $got == "$3" ]]; then echo "PASS $1"; pass=$((pass+1)); else echo "FAIL $1 (exit=$code got=$got)"; fail=$((fail+1)); fi
}
check "write inside out/"        '{"tool_name":"Write","tool_input":{"file_path":"out/customers_masked.csv"}}' allow
check "absolute path inside out" "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$PWD/out/x.csv\"}}" allow
check "overwrite input data"     '{"tool_name":"Write","tool_input":{"file_path":"data/customers.csv"}}' deny
check "path traversal"           '{"tool_name":"Edit","tool_input":{"file_path":"out/../src/shipping.py"}}' deny
check "sibling prefix trick"     '{"tool_name":"Write","tool_input":{"file_path":"outside/evil.txt"}}' deny
check "tool without a path"      '{"tool_name":"Glob","tool_input":{"pattern":"*.py"}}' allow
echo '{not json' | python3 hooks/restrict_writes.py out 2>/dev/null; [[ $? -eq 2 ]] && { echo "PASS malformed payload fails closed"; pass=$((pass+1)); } || { echo "FAIL malformed payload"; fail=$((fail+1)); }
echo "$pass passed, $fail failed"; [[ $fail -eq 0 ]]
