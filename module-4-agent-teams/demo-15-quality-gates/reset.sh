#!/usr/bin/env bash
cd "$(dirname "$0")" && find findings -name '*.md' ! -name TEMPLATE.md -delete && rm -f hooks/gate-log.jsonl && echo "demo-15 reset"
