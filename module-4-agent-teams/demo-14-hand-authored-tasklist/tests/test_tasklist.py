#!/usr/bin/env python3
"""Tests for tools/tasklist.py:  python3 -m unittest tests/test_tasklist.py -v"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, "tools", "tasklist.py")


class TaskListTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.file = os.path.join(self.dir, "tasks.md")
        shutil.copy(os.path.join(ROOT, "fixtures", "tasks-initial.md"), self.file)
        os.makedirs(os.path.join(self.dir, "docs", "api"))

    def tearDown(self):
        shutil.rmtree(self.dir)

    def run_tool(self, *args):
        p = subprocess.run([sys.executable, TOOL, "--file", self.file, *args], capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def write_artifact(self, name):
        with open(os.path.join(self.dir, "docs", "api", name), "w") as f:
            f.write("# doc\n")

    def test_claim_and_double_claim_refused(self):
        self.assertEqual(self.run_tool("claim", "T-001", "a")[0], 0)
        code, out = self.run_tool("claim", "T-001", "b")
        self.assertEqual(code, 1)
        self.assertIn("claimed", out)

    def test_dependency_blocks_claim(self):
        code, out = self.run_tool("claim", "T-006", "a")
        self.assertEqual(code, 1)
        self.assertIn("requires", out)

    def test_done_requires_artifact(self):
        self.run_tool("claim", "T-002", "a")
        self.assertEqual(self.run_tool("done", "T-002", "a")[0], 1)
        self.write_artifact("cart.md")
        self.assertEqual(self.run_tool("done", "T-002", "a")[0], 0)

    def test_only_owner_can_complete(self):
        self.run_tool("claim", "T-002", "a")
        self.write_artifact("cart.md")
        self.assertEqual(self.run_tool("done", "T-002", "b")[0], 1)

    def test_dependency_unblocks_after_all_done(self):
        for i, name in enumerate(["catalog", "cart", "orders", "search", "storage"], 1):
            self.run_tool("claim", f"T-00{i}", "a")
            self.write_artifact(f"{name}.md")
            self.run_tool("done", f"T-00{i}", "a")
        self.assertEqual(self.run_tool("next", "b")[1].strip(), "T-006")

    def test_check_clean_and_broken(self):
        self.assertEqual(self.run_tool("check")[0], 0)
        p = subprocess.run([sys.executable, TOOL, "--file", os.path.join(ROOT, "fixtures", "tasks-broken.md"),
                            "check"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)
        for needle in ["COLLISION: T-003", "multiple owners", "DEADLOCK", "WRITE RACE", "ordering violated"]:
            self.assertIn(needle, p.stdout)

    def test_concurrent_claim_next_never_duplicates(self):
        procs = [subprocess.Popen([sys.executable, TOOL, "--file", self.file, "claim-next", f"w{i}"],
                                  stdout=subprocess.PIPE, text=True) for i in range(10)]
        outs = [p.communicate()[0] for p in procs]
        claimed = [o.split()[1] for o in outs if o.startswith("CLAIMED")]
        self.assertEqual(len(claimed), len(set(claimed)))
        self.assertEqual(sorted(claimed), ["T-001", "T-002", "T-003", "T-004", "T-005"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
