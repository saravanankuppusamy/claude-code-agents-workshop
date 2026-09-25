#!/usr/bin/env python3
"""The lesson's keyword guard (Lesson 3.7.2 / Lab 4), kept for comparison.

Substring matching on the whole command. It works for the obvious cases and fails on:
  * false positives: SELECT drop_date FROM books   /   WHERE title = 'Delete Me Not'
  * false negatives: anything not in the list, e.g. UPDATE, INSERT, ALTER, ATTACH
Run tests/test_hooks.py to see both.
"""
import json
import sys

payload = json.load(sys.stdin)
if payload.get("tool_name") != "Bash":
    sys.exit(0)
command = payload.get("tool_input", {}).get("command", "").upper()
for kw in ["DROP", "DELETE", "TRUNCATE"]:
    if kw in command:
        print(f"BLOCKED: '{kw}' not permitted. Only SELECT is allowed.", file=sys.stderr)
        sys.exit(2)  # exit 2 = hard block; stderr is fed back to Claude
sys.exit(0)
