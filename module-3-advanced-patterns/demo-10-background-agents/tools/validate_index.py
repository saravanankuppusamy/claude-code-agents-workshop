#!/usr/bin/env python3
"""Check the background agent's output before consuming it.
    python3 tools/validate_index.py
Verifies: manifest says done, one record per corpus file, no duplicates, fields valid,
and stars/sentiment agree with the source files (catches hallucinated records).
"""
import glob
import json
import re
import sys

m = json.load(open(".claude/background/manifest.json"))
problems = []
if m.get("status") != "done":
    problems.append(f"manifest status is {m.get('status')!r}, not 'done' - do not consume yet")
files = sorted(glob.glob("corpus/*.md"))
recs = [json.loads(l) for l in open("index/reviews.jsonl") if l.strip()]
seen = [r.get("file", "").split("/")[-1] for r in recs]
if len(recs) != len(files):
    problems.append(f"{len(recs)} records for {len(files)} corpus files")
dups = {s for s in seen if seen.count(s) > 1}
if dups:
    problems.append(f"duplicate records: {sorted(dups)[:5]}")
truth = {}
for f in files:
    txt = open(f).read()
    truth[f.split("/")[-1]] = int(re.search(r"stars:\s*(\d)", txt).group(1))
wrong = 0
for r in recs:
    name = r.get("file", "").split("/")[-1]
    stars = truth.get(name)
    exp = "positive" if stars and stars >= 4 else "negative" if stars and stars <= 2 else "neutral"
    if stars is None or int(r.get("stars", -1)) != stars or r.get("sentiment") != exp:
        wrong += 1
if wrong:
    problems.append(f"{wrong} record(s) disagree with their source file")
print("INDEX OK" if not problems else "INDEX PROBLEMS:\n  - " + "\n  - ".join(problems))
sys.exit(1 if problems else 0)
