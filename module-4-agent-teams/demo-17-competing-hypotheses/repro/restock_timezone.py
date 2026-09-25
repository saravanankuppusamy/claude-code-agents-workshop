#!/usr/bin/env python3
"""Probe H3: can the restock job's timezone handling ever reduce stock?

    python3 repro/restock_timezone.py
Runs restock at times around midnight in several timezones and reports stock before/after.
"""
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fd, path = tempfile.mkstemp(suffix=".json"); os.close(fd)
os.environ["SHOP_STOCK"] = path
from shop import restock, store  # noqa: E402

with open(path, "w") as f:
    json.dump({"isbn-1": 2}, f)
print("time (UTC)            before  after  report file")
for minutes in (-90, -5, 0, 5, 90):
    t = datetime(2026, 9, 20, 0, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)
    before = store.read_stock("isbn-1")
    name = restock.nightly_restock("isbn-1", 5, now=t)
    after = store.read_stock("isbn-1")
    print(f"{t.isoformat():<22}{before:>6}{after:>7}  {name}")
os.remove(path)
print("Stock only ever increases in restock; report file date may differ from UTC date.")
