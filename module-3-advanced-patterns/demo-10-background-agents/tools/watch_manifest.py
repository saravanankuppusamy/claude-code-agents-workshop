#!/usr/bin/env python3
"""Poll a background agent's manifest + heartbeat (Lesson 3.8.4-3.8.5).

    python3 tools/watch_manifest.py            # poll every 3s until done/failed
    python3 tools/watch_manifest.py --once     # print status once (for scripts / CI)

Exit codes: 0 done, 1 failed, 2 stalled (heartbeat older than --stall seconds), 3 not started.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

BG = ".claude/background"


def read_status(stall: int):
    m_path = os.path.join(BG, "manifest.json")
    if not os.path.exists(m_path):
        return 3, "not started (no manifest yet)"
    try:
        m = json.load(open(m_path))
    except ValueError:
        return None, "manifest is being written / partially written - retrying"
    status = m.get("status")
    done, total = m.get("files_done", 0), m.get("files_total", "?")
    if status == "done":
        return 0, f"DONE {done}/{total} -> {m.get('output')}"
    if status == "failed":
        return 1, f"FAILED: {m.get('error')}"
    hb = os.path.join(BG, "heartbeat")
    age = time.time() - os.path.getmtime(hb) if os.path.exists(hb) else None
    if age is not None and age > stall:
        return 2, f"STALLED? running {done}/{total}, last heartbeat {int(age)}s ago"
    return None, f"running {done}/{total} (heartbeat {int(age) if age is not None else '-'}s ago)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--interval", type=float, default=3)
    ap.add_argument("--stall", type=int, default=120)
    a = ap.parse_args()
    while True:
        code, msg = read_status(a.stall)
        print(f"{datetime.now(timezone.utc).strftime('%H:%M:%S')}  {msg}", flush=True)
        if a.once:
            return code if code is not None else 0
        if code is not None and code != 3:
            return code
        time.sleep(a.interval)


if __name__ == "__main__":
    sys.exit(main())
