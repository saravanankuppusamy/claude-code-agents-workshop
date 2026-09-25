#!/usr/bin/env python3
"""TaskCreated gate: enforce task-list discipline on the platform task list.

Every task title must match gates.json "task_title_pattern", e.g.
    T-001: Review app/config.py for insecure defaults -> findings/config.md
so that TaskCompleted can find the artifact, and every task names exactly one output.
Exit 2 prevents creation and tells the lead how to fix the title.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gates_common as g  # noqa: E402

cfg = g.load_config()
payload = g.read_payload()
title = payload.get("task_title") or payload.get("title") or payload.get("subject") or ""
if not title:
    g.log(cfg, "TaskCreated", payload, "allow", "no title field in payload")
    sys.exit(0)
if re.match(cfg["task_title_pattern"], title):
    g.log(cfg, "TaskCreated", payload, "allow")
    sys.exit(0)
msg = (f"Task title '{title}' rejected. Use the form "
       f"'T-###: <what to do> -> findings/<file>.md' (one artifact per task).")
g.log(cfg, "TaskCreated", payload, "block", msg)
print(msg, file=sys.stderr)
sys.exit(2)
