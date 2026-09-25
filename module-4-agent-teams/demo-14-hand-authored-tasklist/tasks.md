# API documentation backfill – shared task list

Teammates change this file ONLY through `python3 tools/tasklist.py` (claim / done / release).
The lead may run `python3 tools/tasklist.py check` at any time.

| task_id | description | status | owner | artifact | requires |
|---|---|---|---|---|---|
| T-001 | Document src/catalog.py | open | | docs/api/catalog.md | |
| T-002 | Document src/cart.py | open | | docs/api/cart.md | |
| T-003 | Document src/orders.py | open | | docs/api/orders.md | |
| T-004 | Document src/search.py | open | | docs/api/search.md | |
| T-005 | Document src/storage.py | open | | docs/api/storage.md | |
| T-006 | Write docs/api/index.md linking all modules with a one-line summary each | open | | docs/api/index.md | T-001, T-002, T-003, T-004, T-005 |
| T-007 | Cross-check every documented signature against the source; list mismatches | open | | docs/api/review.md | T-006 |
