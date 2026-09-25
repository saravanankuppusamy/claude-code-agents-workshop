#!/usr/bin/env python3
"""Keep a state file inside the context budget (Lesson 3.4.6 'context window overgrowth').

    python3 tools/prune_state.py [--keep 10] [.claude/memory/project-state.md]

Moves all but the newest N sessions to .claude/memory/archive/project-state-<date>.md
and inserts a compact "Carried forward" block at the top of the live file containing
every still-open question and every decision from the archived sessions, so nothing
important silently disappears. Writes atomically (temp file + rename) so an interrupted
run can't leave a truncated state file.
"""
import argparse
import os
import re
import tempfile
from datetime import date

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_state import split_sessions  # noqa: E402


def bullets(section: str, field: str) -> list[str]:
    m = re.search(rf"(?m)^- \*\*{field}:\*\*[ \t]*\n((?:[ \t]+- [^\n]*\n?)*)", section)
    if not m:
        return []
    items = [re.sub(r"^[ \t]+- ", "", l).strip() for l in m.group(1).splitlines() if l.strip()]
    return [i for i in items if i.lower() != "none"]


def atomic_write(path: str, text: str):
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".state-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=".claude/memory/project-state.md")
    ap.add_argument("--keep", type=int, default=10)
    a = ap.parse_args()
    text = open(a.path, encoding="utf-8").read()
    title = text.split("## Session ")[0]
    title = re.sub(r"(?ms)^## Carried forward.*?<!-- end-carried -->\n?", "", title)
    sessions = split_sessions(text)
    if len(sessions) <= a.keep:
        print(f"{len(sessions)} sessions - nothing to prune (keep={a.keep})")
        return
    old, recent = sessions[:-a.keep], sessions[-a.keep:]
    archive_dir = os.path.join(os.path.dirname(a.path), "archive")
    os.makedirs(archive_dir, exist_ok=True)
    archive = os.path.join(archive_dir, f"project-state-{date.today().isoformat()}.md")
    with open(archive, "a", encoding="utf-8") as f:
        f.write("".join(old))
    decisions = [d for s in old for d in bullets(s, "decisions")]
    questions = [q for s in old for q in bullets(s, "open_questions")]
    carried = ["## Carried forward (from archived sessions)\n",
               f"_Archived {len(old)} sessions to {os.path.relpath(archive, os.path.dirname(a.path))}_\n\n",
               "**Decisions still in force:**\n"] + [f"- {d}\n" for d in decisions] + \
              ["\n**Open questions (verify still open):**\n"] + [f"- {q}\n" for q in questions] + \
              ["<!-- end-carried -->\n\n"]
    atomic_write(a.path, title.rstrip() + "\n\n" + "".join(carried) + "".join(recent))
    print(f"archived {len(old)} sessions -> {archive}; kept {len(recent)}; carried "
          f"{len(decisions)} decisions and {len(questions)} open questions forward")


if __name__ == "__main__":
    main()
