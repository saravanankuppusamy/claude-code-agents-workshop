#!/usr/bin/env python3
"""A plausible-looking gate with a bug (Lesson 4.8.6 Check Your Understanding).

Bug: it checks for '## Severity:' (with a colon) but the template heading is '## Severity'.
Every artifact fails, every task bounces back to the teammate forever. tests/test_gates.py
contains the 'golden artifact' test that catches this BEFORE a team ever runs.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gates_common as g  # noqa: E402

payload = g.read_payload()
text = str(payload.get("task_title", ""))
m = re.search(r"->\s*([\w./-]+\.md)", text)
if m:
    content = open(os.path.join(g.ROOT, m.group(1))).read() if os.path.exists(os.path.join(g.ROOT, m.group(1))) else ""
    for section in ["## Summary", "## Findings", "## Severity:", "## Recommendation"]:
        if section not in content:
            print(f"missing {section}", file=sys.stderr)
            sys.exit(2)
sys.exit(0)
