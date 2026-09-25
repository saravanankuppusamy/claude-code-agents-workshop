---
name: commit-standards
description: Tidewater commit message format (Conventional-Commit style with required
  scopes). Use when drafting, reviewing or fixing commit messages.
---

# Commit message standards

```
<type>(<scope>): <subject>

<body – optional, 2–4 sentences explaining WHY>

<BREAKING CHANGE: what breaks and how to migrate – only if applicable>
```

- **type**: `feat | fix | refactor | docs | chore | test`
- **scope**: one of `catalog | cart | orders | search | storage | infra`
- **subject**: imperative, present tense, lower-case first word, no trailing period, ≤ 72 chars
- A breaking change puts `BREAKING CHANGE:` as the **first line of the body**.

Validate drafts with:
```bash
python3 .claude/skills/commit-standards/scripts/check_commit_msg.py "<message>"
```

## Examples

```
fix(search): match ISBN-10 input against ISBN-13 records

Customers pasting ISBN-10s from older editions got no results. Normalise both
forms to ISBN-13 before comparing.
```

```
refactor(storage): write orders atomically via temp file and rename

BREAKING CHANGE: storage.save() now requires the data directory to exist; call
storage.init() once at start-up.
```
