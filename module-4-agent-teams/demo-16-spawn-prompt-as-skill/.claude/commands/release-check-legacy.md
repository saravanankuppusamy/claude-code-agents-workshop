---
description: (legacy commands format) Release-readiness team for a version
argument-hint: <version>
allowed-tools: Read, Glob, Grep, Write, Agent
---

Create an agent team to decide whether version $1 is ready to release.

Context gathered when this command runs:
- Files in scope: !`ls src`
- Changelog: @CHANGELOG.md

Spawn test-gap-finder, changelog-verifier and config-auditor as teammates named tests,
changelog and config. Wait until all three findings files exist before writing
findings/release-$1.md with GO/NO-GO on the first line. If the changelog has no $1
section, stop and spawn nobody.
