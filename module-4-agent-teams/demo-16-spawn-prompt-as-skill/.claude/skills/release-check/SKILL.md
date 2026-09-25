---
name: release-check
description: Runs the release-readiness agent team for a version. Invoke manually as
  /release-check <version>.
argument-hint: <version, e.g. 2.4.0>
disable-model-invocation: true
---

Create an agent team to decide whether version **$ARGUMENTS** is ready to release.

## Agents (spawn exactly these, with these names)
- `tests`     – agent type **test-gap-finder**    → findings/test-gaps.md
- `changelog` – agent type **changelog-verifier** → findings/changelog.md (tell it the version is $ARGUMENTS)
- `config`    – agent type **config-auditor**     → findings/config.md
Each teammate writes only its own file.

## Gates
1. Do not start synthesis until all three teammates are idle **and** all three
   findings files exist and are non-empty. Check with Glob; do not assume.
2. If any teammate reports it could not read its inputs, re-run that teammate once.
3. Only then, you (the lead) write `findings/release-$ARGUMENTS.md`:
   - **Decision:** GO or NO-GO on the first line
   - Blockers (with file:line), then non-blocking issues
   - A table of which teammate found what

## Stop conditions
- If CHANGELOG.md has no section for $ARGUMENTS: stop immediately, spawn nobody, and
  say so.
- If any `config` finding is BLOCKER: the decision is NO-GO regardless of other results.
- If a teammate fails twice: stop and report which one and why. Do not synthesise
  from partial results.

Do not fix anything. This is an assessment.
