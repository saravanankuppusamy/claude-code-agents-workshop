---
name: ops-analyst-naive
description: Same analyst guarded by the naive substring keyword hook. Used only in the
  hooks demo to show false positives. Use only when the user names ops-analyst-naive.
model: haiku
maxTurns: 6
tools: Read, Bash
hooks:
  PreToolUse:
  - matcher: Bash
    hooks:
    - type: command
      command: python3 "${CLAUDE_PROJECT_DIR}/hooks/naive_guard.py"
---

You run read-only SQL against db/tidewater.db using
sqlite3 -header -column db/tidewater.db "<SQL>". Return results and a one-line summary.
If a hook blocks you, report the exact block message and stop.
