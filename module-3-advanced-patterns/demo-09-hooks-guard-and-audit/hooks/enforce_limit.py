#!/usr/bin/env python3
"""PreToolUse hook that REWRITES input: add a LIMIT to unbounded SELECTs.

Demonstrates `updatedInput` (Lesson 3.6.2). Runs the full sql_guard check first, so
it is safe to register on its own - a query the guard would deny is denied here too.

    command: python3 "${CLAUDE_PROJECT_DIR}/hooks/enforce_limit.py" --policy policies/marketing.json

The policy's "default_limit" (default 100) is appended to any single SELECT without LIMIT.
Output when rewriting:
    {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow",
      "permissionDecisionReason": "...", "updatedInput": {"command": "<rewritten>"}}}
Note: "allow" also skips the permission prompt for this call - only rewrite calls you
would have approved anyway.
"""
import json
import os
import re
import shlex
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sql_guard  # noqa: E402


def add_limit(command: str, limit: int) -> str | None:
    """Return the rewritten command, or None if no rewrite is needed."""
    changed = False
    out = []
    for tok in shlex.split(command):
        t = tok.strip()
        if re.match(r"(?is)^\s*(SELECT|WITH)\b", t) and not re.search(r"(?i)\bLIMIT\s+\d+", t):
            tok = t.rstrip().rstrip(";") + f" LIMIT {limit};"
            changed = True
        out.append(tok)
    return " ".join(shlex.quote(t) for t in out) if changed else None


def main(argv):
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        print("enforce_limit: unreadable payload - blocking", file=sys.stderr)
        return 2
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    policy = sql_guard.load_policy(argv, project_dir)
    reason = sql_guard.evaluate(payload, policy)
    if reason:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": f"BLOCKED by sql_guard: {reason}"}}))
        return 0
    command = (payload.get("tool_input") or {}).get("command", "")
    if payload.get("tool_name") != "Bash" or "sqlite3" not in command:
        return 0
    rewritten = add_limit(command, int(policy.get("default_limit", 100)))
    if rewritten:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "allow",
            "permissionDecisionReason": f"enforce_limit: added LIMIT {policy.get('default_limit', 100)}",
            "updatedInput": {**payload.get("tool_input", {}), "command": rewritten}}}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
