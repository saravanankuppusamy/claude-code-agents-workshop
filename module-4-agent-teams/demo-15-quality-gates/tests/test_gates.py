#!/usr/bin/env python3
"""Test the team quality gates without running a team.

    python3 -m unittest tests/test_gates.py -v

The most important test is `test_golden_artifact_passes_every_completion_gate`: a gate
that can never pass is worse than no gate (Lesson 4.8.6). The buggy gate fails it.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "tests", "fixtures")


class GateHarness(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        shutil.copy(os.path.join(ROOT, "gates.json"), self.dir)
        os.makedirs(os.path.join(self.dir, "findings"))

    def tearDown(self):
        shutil.rmtree(self.dir)

    def put(self, fixture, dest):
        shutil.copy(os.path.join(FIX, fixture), os.path.join(self.dir, dest))

    def gate(self, script, payload):
        p = subprocess.run([sys.executable, os.path.join(ROOT, "hooks", script)],
                           input=json.dumps(payload), capture_output=True, text=True,
                           env=dict(os.environ, CLAUDE_PROJECT_DIR=self.dir), cwd=self.dir)
        return p.returncode, p.stderr.strip()

    def tasks(self, rows):
        lines = ["| task_id | description | status | owner | artifact | requires |", "|---|---|---|---|---|---|"]
        lines += [f"| {' | '.join(r)} |" for r in rows]
        with open(os.path.join(self.dir, "tasks.md"), "w") as f:
            f.write("\n".join(lines) + "\n")


class TeammateIdleTests(GateHarness):
    def test_unknown_payload_fails_open(self):
        self.assertEqual(self.gate("teammate_idle_gate.py", {})[0], 0)

    def test_plan_phase_allowed(self):
        self.assertEqual(self.gate("teammate_idle_gate.py", {"teammate_name": "config"})[0], 0)

    def test_convention_mode_blocks_bad_artifact(self):
        self.put("missing-severity.md", "findings/uploads.md")
        code, msg = self.gate("teammate_idle_gate.py", {"teammate_name": "uploads"})
        self.assertEqual(code, 2)
        self.assertIn("## Severity", msg)

    def test_convention_mode_allows_good_artifact(self):
        self.put("good.md", "findings/config.md")
        self.assertEqual(self.gate("teammate_idle_gate.py", {"agent_id": "config@sweep"})[0], 0)

    def test_queue_drain(self):
        self.tasks([["T-001", "a", "done", "rev-a", "findings/config.md", ""],
                    ["T-002", "b", "open", "", "findings/uploads.md", ""]])
        self.put("good.md", "findings/config.md")
        code, msg = self.gate("teammate_idle_gate.py", {"teammate_name": "rev-a"})
        self.assertEqual(code, 2)
        self.assertIn("T-002", msg)

    def test_blocked_task_does_not_count_as_eligible(self):
        self.tasks([["T-001", "a", "claimed", "rev-b", "findings/a.md", ""],
                    ["T-002", "b", "open", "", "findings/b.md", "T-001"]])
        self.assertEqual(self.gate("teammate_idle_gate.py", {"teammate_name": "rev-a"})[0], 0)

    def test_claimed_task_blocks_idle(self):
        self.tasks([["T-001", "a", "claimed", "rev-a", "findings/config.md", ""]])
        self.assertEqual(self.gate("teammate_idle_gate.py", {"teammate_name": "rev-a"})[0], 2)

    def test_every_call_is_logged_with_payload(self):
        self.gate("teammate_idle_gate.py", {"teammate_name": "x", "extra_field": 42})
        with open(os.path.join(self.dir, "hooks", "gate-log.jsonl")) as f:
            rec = json.loads(f.readline())
        self.assertEqual(rec["payload"]["extra_field"], 42)


class TaskGateTests(GateHarness):
    def test_task_created_requires_artifact_in_title(self):
        self.assertEqual(self.gate("task_created_gate.py", {"task_title": "Review config"})[0], 2)
        self.assertEqual(self.gate("task_created_gate.py",
                                   {"task_title": "T-001: Review config -> findings/config.md"})[0], 0)

    def test_task_completed_blocks_missing_and_incomplete(self):
        title = {"task_id": "1", "task_title": "T-002: Review uploads -> findings/uploads.md"}
        self.assertEqual(self.gate("task_completed_gate.py", title)[0], 2)          # missing
        self.put("missing-severity.md", "findings/uploads.md")
        code, msg = self.gate("task_completed_gate.py", title)
        self.assertEqual(code, 2)
        self.assertIn("Severity", msg)

    def test_findings_section_needs_items(self):
        self.put("no-items.md", "findings/accounts.md")
        code, msg = self.gate("task_completed_gate.py",
                              {"task_title": "T-003: Review accounts -> findings/accounts.md"})
        self.assertEqual(code, 2)
        self.assertIn("at least", msg)

    def test_golden_artifact_passes_every_completion_gate(self):
        """A known-good artifact must pass. Run this against every gate you write."""
        self.put("good.md", "findings/config.md")
        payload = {"task_title": "T-001: Review config -> findings/config.md"}
        self.assertEqual(self.gate("task_completed_gate.py", payload)[0], 0)

    @unittest.expectedFailure
    def test_golden_artifact_against_buggy_gate(self):
        """Documents the bug: the buggy gate rejects a perfect artifact -> infinite bounce."""
        self.put("good.md", "findings/config.md")
        payload = {"task_title": "T-001: Review config -> findings/config.md"}
        self.assertEqual(self.gate("buggy_task_completed_gate.py", payload)[0], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
