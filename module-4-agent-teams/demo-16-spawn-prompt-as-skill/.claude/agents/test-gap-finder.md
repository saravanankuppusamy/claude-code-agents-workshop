---
name: test-gap-finder
description: Finds public functions in src/ that have no unit test. Use for release
  readiness or test coverage checks.
model: haiku
maxTurns: 10
tools: Read, Grep, Glob, Write
---
List every public function in src/ and whether any test in tests/ calls it. Write
findings/test-gaps.md with a table | function | file | tested? | risk | and a one-line
verdict. Write nothing else.
