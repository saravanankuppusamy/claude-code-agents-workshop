#!/usr/bin/env python3
"""Test every hook in this demo by piping JSON payloads into it - no Claude needed.

    python3 -m unittest tests/test_hooks.py -v        (from the demo folder)

"Test before wiring" (Lesson 3.7.4): each case below is a payload Claude Code would
send, plus the decision we expect. Add a case for every bug report you receive.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOOKS = os.path.join(ROOT, "hooks")
DB = "db/tidewater.db"


def bash(cmd: str) -> dict:
    return {"tool_name": "Bash", "tool_input": {"command": cmd}, "agent_type": "test-agent"}


def sq(sql: str) -> dict:
    return bash(f'sqlite3 {DB} "{sql}"')


def run(script: str, payload, *args, env_root=ROOT):
    data = payload if isinstance(payload, str) else json.dumps(payload)
    env = dict(os.environ, CLAUDE_PROJECT_DIR=env_root)
    p = subprocess.run([sys.executable, os.path.join(HOOKS, script), *args],
                       input=data, capture_output=True, text=True, env=env, cwd=env_root)
    return p.returncode, p.stdout, p.stderr


def decision(script, payload, *args):
    """Normalise a hook result to 'allow' | 'deny' | 'block2' | ('rewrite', cmd)."""
    code, out, err = run(script, payload, *args)
    if code == 2:
        return "block2"
    if out.strip():
        spec = json.loads(out)["hookSpecificOutput"]
        if spec.get("updatedInput"):
            return ("rewrite", spec["updatedInput"]["command"])
        return spec["permissionDecision"]
    return "allow"


OPS = ("--policy", "policies/ops.json")


class SqlGuardTests(unittest.TestCase):
    cases = [
        # (description, payload, expected)
        ("simple select", sq("SELECT isbn, title FROM books LIMIT 5"), "allow"),
        ("lowercase select", sq("select title from books"), "allow"),
        ("join of allowed tables", sq("SELECT o.id, c.name FROM orders o JOIN customers c ON o.customer_id = c.id"), "allow"),
        ("column named drop_date (naive false positive)", sq("SELECT title, drop_date FROM books"), "allow"),
        ("string literal contains DELETE", sq("SELECT isbn FROM books WHERE title = 'Delete Me Not: A Memoir'"), "allow"),
        ("schema dot-command", bash(f'sqlite3 {DB} ".schema books"'), "allow"),
        ("PRAGMA table_info", sq("PRAGMA table_info(orders)"), "allow"),
        ("CTE over allowed table", sq("WITH big AS (SELECT * FROM orders WHERE qty > 2) SELECT count(*) FROM big"), "allow"),
        ("non-sqlite bash is ignored", bash("ls -la db/"), "allow"),
        ("non-Bash tool is ignored", {"tool_name": "Read", "tool_input": {"file_path": "README.md"}}, "allow"),
        ("DROP TABLE", sq("DROP TABLE books"), "deny"),
        ("delete lowercase", sq("delete from orders where id = 1"), "deny"),
        ("UPDATE (naive false negative)", sq("UPDATE books SET price = 0"), "deny"),
        ("INSERT (naive false negative)", sq("INSERT INTO customers VALUES (99,'x','y','z')"), "deny"),
        ("statement smuggling", sq("SELECT 1 FROM books; DROP TABLE books"), "deny"),
        ("sensitive table", sq("SELECT name, salary FROM staff_payroll"), "deny"),
        ("sensitive table in join", sq("SELECT * FROM orders o JOIN staff_payroll s ON s.staff_id = o.customer_id"), "deny"),
        ("sensitive table in subquery", sq("SELECT * FROM books WHERE price > (SELECT min(salary) FROM staff_payroll)"), "deny"),
        ("comma join to sensitive table", sq("SELECT * FROM books, staff_payroll"), "deny"),
        ("dot-command .shell", bash(f'sqlite3 {DB} ".shell rm -rf /"'), "deny"),
        ("ATTACH another database", sq("ATTACH DATABASE 'x.db' AS x"), "deny"),
        ("SQL via pipe hides content", bash(f'echo "DROP TABLE books" | sqlite3 {DB}'), "deny"),
        ("SQL via redirect", bash(f"sqlite3 {DB} < evil.sql"), "deny"),
        ("interactive sqlite", bash(f"sqlite3 {DB}"), "deny"),
        ("chained after harmless command", bash(f'cd . && sqlite3 {DB} "DELETE FROM orders"'), "deny"),
    ]

    def test_cases(self):
        for desc, payload, expected in self.cases:
            with self.subTest(desc):
                self.assertEqual(decision("sql_guard.py", payload, *OPS), expected, desc)

    def test_exit2_mode(self):
        code, _, err = run("sql_guard.py", sq("DROP TABLE books"), *OPS, "--exit2")
        self.assertEqual(code, 2)
        self.assertIn("BLOCKED", err)

    def test_malformed_payload_fails_closed(self):
        code, _, _ = run("sql_guard.py", "{not json", *OPS)
        self.assertEqual(code, 2)

    def test_missing_policy_fails_closed(self):
        code, _, _ = run("sql_guard.py", sq("SELECT 1"), "--policy", "policies/nope.json")
        self.assertEqual(code, 2)

    def test_marketing_policy_is_narrower(self):
        self.assertEqual(decision("sql_guard.py", sq("SELECT name FROM customers"),
                                  "--policy", "policies/marketing.json"), "deny")


class NaiveGuardTests(unittest.TestCase):
    """Documents the naive guard's known failures - these assertions are the lesson."""

    def test_false_positive_on_column_name(self):
        self.assertEqual(decision("naive_guard.py", sq("SELECT title, drop_date FROM books")), "block2")

    def test_false_positive_on_string_literal(self):
        self.assertEqual(decision("naive_guard.py", sq("SELECT isbn FROM books WHERE title = 'Delete Me Not'")), "block2")

    def test_false_negative_on_update(self):
        self.assertEqual(decision("naive_guard.py", sq("UPDATE books SET price = 0")), "allow")


class EnforceLimitTests(unittest.TestCase):
    MK = ("--policy", "policies/marketing.json")

    def test_adds_limit(self):
        result = decision("enforce_limit.py", sq("SELECT title FROM books"), *self.MK)
        self.assertEqual(result[0], "rewrite")
        self.assertIn("LIMIT 50", result[1])

    def test_keeps_existing_limit(self):
        self.assertEqual(decision("enforce_limit.py", sq("SELECT title FROM books LIMIT 3"), *self.MK), "allow")

    def test_still_denies_writes(self):
        self.assertEqual(decision("enforce_limit.py", sq("DELETE FROM books"), *self.MK), "deny")

    def test_rewritten_command_is_still_valid_shell(self):
        _, cmd = decision("enforce_limit.py", sq("SELECT title FROM books WHERE price > 10"), *self.MK)
        out = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
        if shutil.which("sqlite3"):
            self.assertEqual(out.returncode, 0, out.stderr)


class AuditLogTests(unittest.TestCase):
    def test_writes_jsonl_record(self):
        tmp = tempfile.mkdtemp()
        payload = dict(sq("SELECT count(*) FROM books"), tool_response={"stdout": "12\n"},
                       duration_ms=4, session_id="s1")
        code, out, _ = run("audit_log.py", payload, env_root=tmp)
        self.assertEqual((code, out), (0, ""))  # silent: agent sees original output
        with open(os.path.join(tmp, "audit", "query-audit.jsonl")) as f:
            rec = json.loads(f.readline())
        self.assertEqual(rec["agent_type"], "test-agent")
        self.assertEqual(rec["result_preview"], "12\n")
        self.assertEqual(rec["duration_ms"], 4)
        shutil.rmtree(tmp)


class RateLimitTests(unittest.TestCase):
    def test_sixth_call_blocked(self):
        tmp = tempfile.mkdtemp()
        codes = [run("rate_limit.py", bash("ls"), "--max", "5", "--window", "60", env_root=tmp)[0]
                 for _ in range(6)]
        self.assertEqual(codes, [0, 0, 0, 0, 0, 2])
        _, _, err = run("rate_limit.py", bash("ls"), "--max", "5", "--window", "60", env_root=tmp)
        self.assertIn("please wait", err)
        shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main(verbosity=2)
