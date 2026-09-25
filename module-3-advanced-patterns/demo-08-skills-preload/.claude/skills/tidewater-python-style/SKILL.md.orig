---
name: tidewater-python-style
description: Tidewater Books Python style rules (naming, function length, error
  handling, docstrings). Use when writing, reviewing or refactoring Python in this repo.
---

# Tidewater Python style (v3)

Apply these rules to every piece of Python you write or review. When reporting a
violation, cite the rule ID.

| ID | Rule |
|---|---|
| TW-N1 | Functions and variables use `snake_case`. |
| TW-N2 | Module-level constants use `UPPER_SNAKE_CASE`. |
| TW-N3 | Classes use `PascalCase`. |
| TW-F1 | A function body is at most **20 lines** (excluding docstring and blank lines). |
| TW-E1 | File I/O, network and database calls are wrapped in `try/except` with a *specific* exception type – never bare `except:`. |
| TW-E2 | Files are opened with a `with` block. |
| TW-D1 | Every public function has a one-line docstring. |

## Deterministic check

Before giving a verdict, run the bundled checker and use its output as ground truth
for rules it covers (it does not judge naming quality, only form):

```bash
python3 .claude/skills/tidewater-python-style/scripts/check_style.py <file.py> [--max-lines N]
```

Report findings as: `RULE-ID  file:line  function/name  – one-line explanation`.
