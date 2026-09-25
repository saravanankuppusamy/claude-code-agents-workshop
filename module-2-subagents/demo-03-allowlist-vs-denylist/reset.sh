#!/usr/bin/env bash
# Restore src/inventory.py after the demo (the denylist reviewer may have edited it).
cd "$(dirname "$0")" && cp src/inventory.py.orig src/inventory.py && echo "inventory.py restored"
