#!/usr/bin/env python3
"""Show WHY the claim tool locks: 8 'teammates' race to claim tasks at the same moment.

    python3 tools/race_demo.py naive     # read-modify-write with no lock -> duplicate claims
    python3 tools/race_demo.py locked    # tasklist.py claim-next           -> never duplicates

Runs on a temporary copy of fixtures/tasks-initial.md; your tasks.md is untouched.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from multiprocessing import Barrier, Process

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tasklist  # noqa: E402


def naive_claim(path, owner, barrier):
    barrier.wait()
    rows_text = open(path).read()                      # 1. read
    prefix, header, rows, suffix = tasklist.parse(rows_text)
    el = tasklist.eligible(rows)
    if not el:
        return
    time.sleep(0.01)                                    # 2. "think" (the model deciding)
    target = el[0]["task_id"]
    with open(path + ".claims", "a") as log:           # record what we believe we claimed
        log.write(f"{target} {owner}\n")
    el[0]["status"], el[0]["owner"] = "claimed", owner
    open(path, "w").write(tasklist.render(prefix, header, rows, suffix))   # 3. write (last wins)


def locked_claim(path, owner, barrier):
    barrier.wait()
    out = subprocess.run([sys.executable, os.path.join(HERE, "tasklist.py"), "--file", path,
                          "claim-next", owner], capture_output=True, text=True).stdout
    m = re.search(r"CLAIMED (T-\d+)", out)
    if m:
        with open(path + ".claims", "a") as log:
            log.write(f"{m.group(1)} {owner}\n")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "naive"
    tmp = tempfile.mkdtemp()
    path = os.path.join(tmp, "tasks.md")
    shutil.copy(os.path.join(HERE, "..", "fixtures", "tasks-initial.md"), path)
    n = 8
    barrier = Barrier(n)
    target = naive_claim if mode == "naive" else locked_claim
    procs = [Process(target=target, args=(path, f"writer-{i}", barrier)) for i in range(n)]
    [p.start() for p in procs]
    [p.join() for p in procs]
    claims = open(path + ".claims").read().split("\n") if os.path.exists(path + ".claims") else []
    claims = [c.split() for c in claims if c.strip()]
    by_task = {}
    for t, o in claims:
        by_task.setdefault(t, []).append(o)
    print(f"mode={mode}: {len(claims)} teammates believe they claimed a task")
    for t in sorted(by_task):
        flag = "   <-- DUPLICATE WORK" if len(by_task[t]) > 1 else ""
        print(f"  {t}: {', '.join(by_task[t])}{flag}")
    final = tasklist.read(path)[2]
    print("final file says:", ", ".join(f"{r['task_id']}={r['owner'] or '-'}" for r in final if r["owner"]))
    shutil.rmtree(tmp)
    return 1 if any(len(v) > 1 for v in by_task.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
