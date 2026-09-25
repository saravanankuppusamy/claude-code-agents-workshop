#!/usr/bin/env bash
# Reset demo 07 to its starting state.
cd "$(dirname "$0")"
cp tests/fixtures/seed-state.md .claude/memory/project-state.md
rm -rf .claude/agent-memory .claude/agent-memory-local .claude/memory/archive
echo "demo-07 reset: state file restored, platform memory cleared"
