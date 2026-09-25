#!/usr/bin/env bash
cd "$(dirname "$0")" && cp fixtures/tasks-initial.md tasks.md && rm -f docs/api/*.md tasks.md.lock && echo "demo-14 reset"
