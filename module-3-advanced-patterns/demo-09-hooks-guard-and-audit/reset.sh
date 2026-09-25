#!/usr/bin/env bash
cd "$(dirname "$0")" && python3 setup_db.py && rm -rf audit/*.jsonl .hook-state && echo "demo-09 reset"
