#!/usr/bin/env python3
"""PreToolUse hook: deny any Write/Edit whose target is outside an allowed directory.

Usage (in agent frontmatter):
    command: python3 "${CLAUDE_PROJECT_DIR}/hooks/restrict_writes.py" out [other-dir ...]

Uses the structured JSON decision (exit 0 + hookSpecificOutput) so the agent gets a
clear reason, and falls back to allowing any tool without a file path.
"""
import json
import os
import sys


def decide(payload: dict, allowed_dirs: list[str], project_dir: str) -> dict | None:
    tool_input = payload.get("tool_input") or {}
    target = tool_input.get("file_path") or tool_input.get("notebook_path") or tool_input.get("path")
    if not target:
        return None  # nothing to check
    target_abs = os.path.realpath(os.path.join(project_dir, target))
    for d in allowed_dirs:
        root = os.path.realpath(os.path.join(project_dir, d))
        if target_abs == root or target_abs.startswith(root + os.sep):
            return None
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"Write to {target} blocked by restrict_writes.py: this agent may only "
                f"write under {', '.join(d + '/' for d in allowed_dirs)}"
            ),
        }
    }


def main() -> int:
    allowed = sys.argv[1:] or ["out"]
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        print("restrict_writes: unreadable payload - blocking to be safe", file=sys.stderr)
        return 2  # fail CLOSED for a security control
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    decision = decide(payload, allowed, project_dir)
    if decision:
        print(json.dumps(decision))
    return 0


if __name__ == "__main__":
    sys.exit(main())
