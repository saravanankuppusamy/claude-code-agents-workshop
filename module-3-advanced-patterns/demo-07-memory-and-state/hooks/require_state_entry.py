#!/usr/bin/env python3
"""SubagentStop gate: don't let session-tracker stop without a fresh state entry.

Registered as a `Stop` hook in the agent's frontmatter; Claude Code converts a
subagent's Stop hook to SubagentStop. Exit 2 blocks the stop and feeds stderr back
to the agent, which then writes the entry. Exit 0 lets it stop.

Only enforces when the agent was asked to wrap up (the transcript's last user
message mentions wrap up / end session / record) - a startup briefing may stop freely.
Guards against infinite loops with `stop_hook_active`.
"""
import json
import os
import re
import sys
import time

STATE = ".claude/memory/project-state.md"
FRESH_SECONDS = 15 * 60
WRAP_UP = re.compile(r"wrap\s*up|end\s+(the\s+)?session|record\s+(the\s+)?session", re.I)


def last_user_text(transcript_path: str) -> str:
    try:
        with open(transcript_path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return ""
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        msg = entry.get("message") or {}
        if entry.get("type") == "user" or msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, list):
                content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
            if content:
                return str(content)
    return ""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if payload.get("stop_hook_active"):
        return 0  # we already blocked once; never loop forever
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    transcript = payload.get("agent_transcript_path") or payload.get("transcript_path") or ""
    if transcript and not WRAP_UP.search(last_user_text(transcript)):
        return 0  # not a wrap-up request
    path = os.path.join(root, STATE)
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < FRESH_SECONDS:
        return 0
    print("Before you stop: append this session's entry to .claude/memory/project-state.md "
          "using the schema in .claude/memory/state-template.md, then confirm.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
