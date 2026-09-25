#!/usr/bin/env python3
"""Validate a file-backed state file against the session schema.

    python3 tools/validate_state.py [.claude/memory/project-state.md]

Detects the failure modes from Lesson 3.4.6 that a script *can* detect:
  - corrupted structure (truncated entry: no <!-- end-session --> marker)
  - missing / out-of-order fields (schema drift)
  - bad dates, future dates
  - context overgrowth (too many entries / too many bytes)
Exit 0 = valid, 1 = problems found.
"""
import re
import sys
from datetime import date

FIELDS = ["date", "agent", "files_examined", "work_completed", "decisions", "open_questions"]
MAX_ENTRIES = 30
MAX_BYTES = 25_000


def split_sessions(text: str):
    parts = re.split(r"(?m)^## Session ", text)
    return ["## Session " + p for p in parts[1:]]


def check(text: str) -> list[str]:
    problems = []
    sessions = split_sessions(text)
    if len(text.encode()) > MAX_BYTES:
        problems.append(f"file is {len(text.encode())} bytes (> {MAX_BYTES}); prune with tools/prune_state.py")
    if len(sessions) > MAX_ENTRIES:
        problems.append(f"{len(sessions)} sessions (> {MAX_ENTRIES}); prune with tools/prune_state.py")
    for i, s in enumerate(sessions, 1):
        header = s.splitlines()[0]
        if "<!-- end-session -->" not in s:
            problems.append(f"session {i} ({header}): truncated - no end-session marker")
        found = re.findall(r"(?m)^- \*\*(\w+):\*\*", s)
        missing = [f for f in FIELDS if f not in found]
        if missing:
            problems.append(f"session {i} ({header}): missing fields {missing}")
        elif found[:len(FIELDS)] != FIELDS:
            problems.append(f"session {i} ({header}): fields out of order {found}")
        m = re.search(r"(?m)^- \*\*date:\*\*\s*(\S+)", s)
        if m:
            try:
                d = date.fromisoformat(m.group(1))
                if d > date.today():
                    problems.append(f"session {i}: date {d} is in the future")
            except ValueError:
                problems.append(f"session {i}: date '{m.group(1)}' is not ISO-8601")
    return problems


def main(argv):
    path = argv[0] if argv else ".claude/memory/project-state.md"
    with open(path, encoding="utf-8") as f:
        text = f.read()
    problems = check(text)
    n = len(split_sessions(text))
    if problems:
        print(f"INVALID  {path}  ({n} sessions)")
        for p in problems:
            print("  -", p)
        return 1
    print(f"VALID    {path}  ({n} sessions)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
