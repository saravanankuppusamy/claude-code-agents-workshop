#!/usr/bin/env python3
"""Validate a commit message against the commit-standards skill.
    python3 check_commit_msg.py "feat(cart): add gift wrap"      # or pipe via stdin
"""
import re
import sys

TYPES = "feat|fix|refactor|docs|chore|test"
SCOPES = "catalog|cart|orders|search|storage|infra"
HEADER = re.compile(rf"^(?P<type>{TYPES})\((?P<scope>{SCOPES})\): (?P<subject>.+)$")


def check(msg: str) -> list[str]:
    lines = msg.strip("\n").splitlines()
    if not lines:
        return ["empty message"]
    errs = []
    m = HEADER.match(lines[0])
    if not m:
        errs.append(f"header must be <type>(<scope>): <subject> with type in [{TYPES}] and scope in [{SCOPES}]")
    else:
        s = m.group("subject")
        if len(lines[0]) > 72:
            errs.append(f"header is {len(lines[0])} chars (> 72)")
        if s.endswith("."):
            errs.append("subject must not end with a period")
        if s[:1].isupper():
            errs.append("subject should start lower-case")
        if re.match(r"^\w+(ed|ing)\b", s):
            errs.append("subject should be imperative ('add', not 'added'/'adding')")
    if len(lines) > 1 and lines[1].strip():
        errs.append("line 2 must be blank")
    body = [l for l in lines[2:] if l.strip()]
    if any("BREAKING CHANGE" in l for l in body) and not body[0].startswith("BREAKING CHANGE:"):
        errs.append("BREAKING CHANGE: must be the first line of the body")
    return errs


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    errs = check(msg)
    print("OK" if not errs else "\n".join("FAIL: " + e for e in errs))
    sys.exit(1 if errs else 0)
