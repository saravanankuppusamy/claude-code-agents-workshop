#!/usr/bin/env python3
"""Generate a 60-session state file to demo pruning:  python3 tests/make_big_state.py > /tmp/big.md"""
from datetime import date, timedelta
d0 = date(2026, 6, 1)
print("# project-state.md – generated\n")
for i in range(60):
    d = d0 + timedelta(days=i)
    q = f"  - Is cache TTL {i} minutes right?" if i % 7 == 0 else "  - none"
    print(f"## Session {d} 09:00\n\n- **date:** {d}\n- **agent:** session-tracker\n"
          f"- **files_examined:** src/search.py\n- **work_completed:** Session {i}.\n"
          f"- **decisions:**\n  - Decision number {i}\n- **open_questions:**\n{q}\n<!-- end-session -->\n")
