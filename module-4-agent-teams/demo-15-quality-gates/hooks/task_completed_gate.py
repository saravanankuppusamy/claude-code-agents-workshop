#!/usr/bin/env python3
"""TaskCompleted gate: a task may only be marked complete if its artifact passes.

The artifact path is read from the task title ("... -> findings/x.md", enforced by
task_created_gate.py). Exit 2 blocks completion; stderr becomes the teammate's feedback.
Designed to be idempotent: it only reads, so it can run any number of times.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gates_common as g  # noqa: E402

cfg = g.load_config()
payload = g.read_payload()
text = " ".join(str(payload.get(k, "")) for k in ("task_title", "title", "subject", "task_description", "description"))
m = re.search(r"->\s*([\w./-]+\.md)", text)
if not m:
    g.log(cfg, "TaskCompleted", payload, "allow", "no artifact named in task - nothing to validate")
    sys.exit(0)
problems = g.validate_artifact(cfg, m.group(1))
if problems:
    msg = "Cannot complete yet: " + "; ".join(problems)
    g.log(cfg, "TaskCompleted", payload, "block", msg)
    print(msg, file=sys.stderr)
    sys.exit(2)
g.log(cfg, "TaskCompleted", payload, "allow", f"{m.group(1)} valid")
sys.exit(0)
