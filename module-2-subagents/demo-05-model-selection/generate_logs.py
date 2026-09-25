#!/usr/bin/env python3
"""Generate a deterministic set of noisy application logs for the model-selection demo.

    python3 generate_logs.py            # 20 files x 400 lines in logs/
    python3 generate_logs.py 200 1000   # bigger run for a timing comparison

Planted signal (the "answer key") is printed at the end so the instructor can grade
each model's findings.
"""
import os, random, sys
from datetime import datetime, timedelta

files = int(sys.argv[1]) if len(sys.argv) > 1 else 20
lines = int(sys.argv[2]) if len(sys.argv) > 2 else 400
random.seed(42)
os.makedirs("logs", exist_ok=True)

NOISE = [
    "INFO  http GET /books/{isbn} 200 {ms}ms",
    "INFO  http GET /search?q=sea 200 {ms}ms",
    "DEBUG cache hit key=book:{isbn}",
    "INFO  cart updated customer={cid} items=2",
    "WARN  slow query books_by_author {ms}ms",
]
PLANTED = [
    # (probability, template)  -- the real incidents
    (0.004, "ERROR payment-gateway timeout after 30000ms order={oid} provider=stripe-eu"),
    (0.002, "ERROR inventory negative stock isbn={isbn} qty=-1 after concurrent decrement"),
    (0.001, "ERROR storage write failed: [Errno 28] No space left on device path=data/orders.json"),
]
start = datetime(2026, 9, 1, 8, 0, 0)
counts = {t: 0 for _, t in PLANTED}
for n in range(files):
    t = start + timedelta(hours=n)
    with open(f"logs/app-{n:03d}.log", "w") as f:
        for _ in range(lines):
            t += timedelta(seconds=random.randint(1, 9))
            tpl = random.choice(NOISE)
            for p, planted in PLANTED:
                if random.random() < p:
                    tpl = planted
                    counts[planted] += 1
                    break
            msg = tpl.format(isbn=random.randint(10**12, 10**13 - 1), ms=random.randint(5, 900),
                             cid=random.randint(1, 5000), oid=random.randint(1, 99999))
            f.write(f"{t.isoformat()} {msg}\n")
print(f"wrote {files} files x {lines} lines to logs/")
print("ANSWER KEY (planted error patterns):")
for tpl, c in counts.items():
    print(f"  {c:4d}  {tpl.split(' order=')[0].split(' isbn=')[0].split(' path=')[0]}")
