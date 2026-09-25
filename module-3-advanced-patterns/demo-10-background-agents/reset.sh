#!/usr/bin/env bash
cd "$(dirname "$0")" && rm -rf .claude/background/* index/* && python3 make_corpus.py && echo "demo-10 reset"
