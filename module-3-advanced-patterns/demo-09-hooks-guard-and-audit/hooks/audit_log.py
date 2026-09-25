#!/usr/bin/env python3
"""PostToolUse hook: append a structured audit record for every executed Bash call.

Writes JSON Lines to audit/query-audit.jsonl (one object per line - easy to grep, jq,
or load into a dashboard). Records WHO (agent_type/agent_id/session), WHAT (command),
HOW LONG (duration_ms) and a preview of the RESULT (tool_response).

Prints nothing on stdout, so the agent sees the original tool output unchanged.
A blocked PreToolUse call never reaches this hook - the log only shows what ran.
"""
import json
import os
import sys
from datetime import datetime, timezone

PREVIEW = 300


def response_text(payload: dict) -> str:
    # Field name / shape varies by tool and version: read defensively.
    r = payload.get("tool_response", payload.get("tool_output", ""))
    if isinstance(r, dict):
        r = r.get("stdout") or r.get("output") or json.dumps(r)
    return str(r)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0  # never break the session because logging failed
    if payload.get("tool_name") != "Bash":
        return 0
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    out = response_text(payload)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session_id": payload.get("session_id"),
        "agent_type": payload.get("agent_type", "main"),
        "agent_id": payload.get("agent_id"),
        "effort": (payload.get("effort") or {}).get("level") if isinstance(payload.get("effort"), dict)
                  else payload.get("effort"),
        "command": (payload.get("tool_input") or {}).get("command", ""),
        "duration_ms": payload.get("duration_ms"),
        "result_lines": out.count("\n") + (1 if out and not out.endswith("\n") else 0),
        "result_preview": out[:PREVIEW],
    }
    os.makedirs(os.path.join(root, "audit"), exist_ok=True)
    with open(os.path.join(root, "audit", "query-audit.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
