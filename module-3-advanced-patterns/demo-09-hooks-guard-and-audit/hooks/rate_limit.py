#!/usr/bin/env python3
"""PreToolUse hook: at most N Bash calls per rolling window (Lab 4 Challenge 2 solution).

    command: python3 "${CLAUDE_PROJECT_DIR}/hooks/rate_limit.py" --max 5 --window 60

Hooks are separate processes with no shared memory, so state is externalised to a
file (.hook-state/rate-<agent>.json) - the same idea as file-backed agent state.
An fcntl lock makes read-modify-write safe when two tool calls fire at once.
"""
import argparse
import fcntl
import json
import os
import sys
import time


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=5)
    ap.add_argument("--window", type=int, default=60)
    args = ap.parse_args()
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    agent = payload.get("agent_type") or "main"
    state_dir = os.path.join(root, ".hook-state")
    os.makedirs(state_dir, exist_ok=True)
    path = os.path.join(state_dir, f"rate-{agent}.json")
    now = time.time()
    with open(path, "a+", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)           # serialise concurrent hook processes
        f.seek(0)
        try:
            stamps = json.load(f)
        except ValueError:
            stamps = []
        stamps = [t for t in stamps if now - t < args.window]
        if len(stamps) >= args.max:
            wait = int(args.window - (now - min(stamps))) + 1
            print(f"Rate limit reached – please wait {wait} seconds "
                  f"({args.max} Bash calls per {args.window}s for {agent})", file=sys.stderr)
            return 2
        stamps.append(now)
        f.seek(0)
        f.truncate()
        json.dump(stamps, f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
