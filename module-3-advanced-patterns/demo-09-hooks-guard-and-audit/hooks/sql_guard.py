#!/usr/bin/env python3
"""
sql_guard.py - PreToolUse hook: allow only read-only SQL against allowlisted tables.

This is the "production-minded" version of the keyword guard from Lesson 3.7 / Lab 4.
It fixes the failure modes the lesson calls out:

  * false positives      - keywords are matched as whole words, AFTER string literals
                           and comments are removed (so `drop_date` and the title
                           'Delete Me Not' are fine)
  * statement smuggling  - `SELECT 1; DROP TABLE x` is split and every statement checked
  * table exposure       - every table after FROM/JOIN must be on the policy allowlist
  * sqlite dot-commands  - `.shell`, `.system`, `.import`, `.output` ... are blocked
  * evasion              - sqlite3 fed by a pipe / redirect / heredoc is blocked
                           (we can't see the SQL, so we fail CLOSED)

Policy is per-agent: pass a JSON policy file as an argument, e.g.
    command: python3 "${CLAUDE_PROJECT_DIR}/hooks/sql_guard.py" --policy policies/ops.json

Decision output (exit 0 + JSON):
    {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": "..."}}
Pass --exit2 to block the classic way instead (exit 2, reason on stderr).

Test without Claude:
    echo '{"tool_name":"Bash","tool_input":{"command":"sqlite3 db/tidewater.db \\"DROP TABLE books\\""}}' \
      | python3 hooks/sql_guard.py --policy policies/ops.json
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys

WRITE_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "REPLACE", "TRUNCATE",
    "ATTACH", "DETACH", "VACUUM", "REINDEX", "GRANT", "REVOKE", "UPSERT",
}
READ_STARTS = {"SELECT", "WITH", "EXPLAIN"}
DEFAULT_POLICY = {
    "allowed_tables": [],
    "allowed_dot_commands": [".schema", ".tables"],
    "max_statements": 1,
}


# ----------------------------------------------------------------------------- helpers
def load_policy(argv: list[str], project_dir: str) -> dict:
    policy = dict(DEFAULT_POLICY)
    if "--policy" in argv:
        path = argv[argv.index("--policy") + 1]
        if not os.path.isabs(path):
            path = os.path.join(project_dir, path)
        with open(path, encoding="utf-8") as f:
            policy.update(json.load(f))
    policy["allowed_tables"] = {t.lower() for t in policy["allowed_tables"]}
    return policy


def strip_literals_and_comments(sql: str) -> str:
    """Replace '...' strings, "..." identifiers-as-strings and comments with spaces."""
    sql = re.sub(r"--[^\n]*", " ", sql)
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    sql = re.sub(r"'(?:[^']|'')*'", "''", sql)
    return sql


def split_statements(sql: str) -> list[str]:
    return [s.strip() for s in sql.split(";") if s.strip()]


def referenced_tables(sql: str) -> set[str]:
    """Tables after FROM / JOIN (incl. comma-joined lists). Simple on purpose - see README."""
    tables = set()
    for m in re.finditer(r"\b(?:FROM|JOIN)\s+([^;]+?)(?=\bWHERE\b|\bGROUP\b|\bORDER\b|\bLIMIT\b|"
                         r"\bON\b|\bJOIN\b|\bINNER\b|\bLEFT\b|\bRIGHT\b|\bCROSS\b|\bUNION\b|\)|$)",
                         sql, flags=re.I | re.S):
        for part in m.group(1).split(","):
            words = part.strip().split()
            if not words:
                continue
            name = words[0].strip('"`[]').lower()
            if name and name != "(" and not name.startswith("("):
                tables.add(name.split(".")[-1])
    return tables


def extract_sqlite_calls(command: str):
    """Yield (ok, sql_or_reason) for every sqlite3 invocation in a shell command."""
    if not re.search(r"\bsqlite3\b", command):
        return
    # Anything that feeds sqlite3 via stdin hides the SQL from us -> fail closed.
    if re.search(r"\|\s*sqlite3\b|\bsqlite3\b[^|;&]*<", command):
        yield False, "sqlite3 must receive SQL as a quoted argument, not via a pipe, redirect or heredoc"
        return
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        yield False, "could not parse the shell command (unbalanced quotes?)"
        return
    for i, tok in enumerate(tokens):
        if os.path.basename(tok) != "sqlite3":
            continue
        args = [t for t in tokens[i + 1:]]
        # stop at the next shell control operator
        for j, t in enumerate(args):
            if t in {"&&", "||", ";", "|"}:
                args = args[:j]
                break
        positional = [a for a in args if not a.startswith("-")]
        if len(positional) < 2:
            yield False, "interactive sqlite3 (no SQL argument) is not allowed"
            continue
        yield True, " ".join(positional[1:])


def check_sql(sql: str, policy: dict) -> str | None:
    """Return a denial reason, or None if the SQL is allowed."""
    stripped = sql.strip()
    if stripped.startswith("."):
        cmd = stripped.split()[0].lower()
        if cmd in policy["allowed_dot_commands"]:
            return None
        return f"sqlite dot-command '{cmd}' is not allowed (allowed: {', '.join(policy['allowed_dot_commands'])})"

    clean = strip_literals_and_comments(sql)
    statements = split_statements(clean)
    if not statements:
        return "empty SQL"
    if len(statements) > policy["max_statements"]:
        return f"{len(statements)} statements in one call; max is {policy['max_statements']}"
    for st in statements:
        words = re.findall(r"[A-Za-z_]+", st.upper())
        if not words:
            return "could not find a SQL keyword"
        first = words[0]
        if first == "PRAGMA":
            if re.match(r"(?i)^\s*PRAGMA\s+table_info\s*\(", st):
                continue
            return "only PRAGMA table_info(...) is allowed"
        if first not in READ_STARTS:
            return f"statement starts with {first}; only SELECT / WITH are allowed"
        bad = WRITE_KEYWORDS.intersection(words)
        if bad:
            return f"write keyword(s) {', '.join(sorted(bad))} not permitted; read-only queries only"
        if policy["allowed_tables"]:
            tables = referenced_tables(st)
            # CTE names defined in WITH are not real tables
            ctes = {m.lower() for m in re.findall(r"(?i)\b(\w+)\s+AS\s*\(", st)}
            blocked = sorted(t for t in tables - ctes if t not in policy["allowed_tables"])
            if blocked:
                return (f"table(s) {', '.join(blocked)} not on this agent's allowlist "
                        f"({', '.join(sorted(policy['allowed_tables']))})")
    return None


def evaluate(payload: dict, policy: dict) -> str | None:
    if payload.get("tool_name") != "Bash":
        return None
    command = (payload.get("tool_input") or {}).get("command", "")
    for ok, value in extract_sqlite_calls(command):
        if not ok:
            return value
        reason = check_sql(value, policy)
        if reason:
            return reason
    return None


# ----------------------------------------------------------------------------- main
def main(argv: list[str]) -> int:
    use_exit2 = "--exit2" in argv
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        print("sql_guard: unreadable hook payload - blocking (fail closed)", file=sys.stderr)
        return 2
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    try:
        policy = load_policy(argv, project_dir)
    except (OSError, ValueError, IndexError) as exc:
        print(f"sql_guard: cannot load policy ({exc}) - blocking (fail closed)", file=sys.stderr)
        return 2

    reason = evaluate(payload, policy)
    if reason is None:
        return 0
    reason = f"BLOCKED by sql_guard: {reason}"
    if use_exit2:
        print(reason, file=sys.stderr)
        return 2
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
