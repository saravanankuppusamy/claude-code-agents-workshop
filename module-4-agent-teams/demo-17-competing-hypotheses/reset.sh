#!/usr/bin/env bash
cd "$(dirname "$0")" && find findings -name '*.md' ! -name TEMPLATE.md -delete && rm -f rca-report.md && echo "demo-17 reset"
