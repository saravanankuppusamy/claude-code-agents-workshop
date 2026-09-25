#!/usr/bin/env python3
"""
tasklist.py - safe operations on a hand-authored Markdown task list (Lesson 4.4.3-4.6).

The lesson notes that a Markdown task list "has no transactional write mechanism", so
two teammates can claim the same task. This tool gives teammates ONE way to change the
list: every write takes an exclusive file lock, re-reads the file, validates the
transition, and replaces the file atomically. Collisions become impossible instead of
merely detectable.

    python3 tools/tasklist.py show                      # table + what is claimable
    python3 tools/tasklist.py next  <owner>             # first eligible task for owner
    python3 tools/tasklist.py claim <task_id> <owner>   # open -> claimed (atomic)
    python3 tools/tasklist.py claim-next <owner>        # next + claim in one locked step
    python3 tools/tasklist.py done  <task_id> <owner>   # claimed -> done (artifact must exist)
    python3 tools/tasklist.py release <task_id> <owner> # claimed -> open
    python3 tools/tasklist.py check                     # lead's integrity/collision check
    python3 tools/tasklist.py reset                     # every task -> open, no owner

Options: --file tasks.md (default: tasks.md in the current directory)

Table format (column names are the team's convention - Lesson 4.4.4):
| task_id | description | status | owner | artifact | requires |
`requires` may list several ids separated by commas.
Exit codes: 0 ok, 1 refused (with reason on stderr), 2 usage error.
"""
from __future__ import annotations

import fcntl
import os
import re
import sys
import tempfile
from contextlib import contextmanager

COLUMNS = ["task_id", "description", "status", "owner", "artifact", "requires"]
STATUSES = {"open", "claimed", "done"}


# ----------------------------------------------------------------------------- io
def parse(text: str):
    """Return (prefix_lines, header_cols, rows, suffix_lines)."""
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.strip().startswith("|")), None)
    if start is None:
        raise ValueError("no Markdown table found")
    end = start
    while end < len(lines) and lines[end].strip().startswith("|"):
        end += 1
    table = lines[start:end]
    header = [c.strip().lower().replace(" ", "_") for c in table[0].strip().strip("|").split("|")]
    rows = []
    for line in table[2:]:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        cells += [""] * (len(header) - len(cells))
        rows.append(dict(zip(header, cells)))
    return lines[:start], header, rows, lines[end:]


def render(prefix, header, rows, suffix) -> str:
    widths = {h: max(len(h), *(len(r.get(h, "")) for r in rows)) if rows else len(h) for h in header}
    fmt = lambda vals: "| " + " | ".join(v.ljust(widths[h]) for h, v in zip(header, vals)) + " |"
    out = prefix + [fmt(header), "|" + "|".join("-" * (widths[h] + 2) for h in header) + "|"]
    out += [fmt([r.get(h, "") for h in header]) for r in rows]
    return "\n".join(out + suffix) + "\n"


@contextmanager
def locked(path: str):
    """Exclusive lock on a sidecar file, then yield parsed table; caller may mutate."""
    lock_path = path + ".lock"
    with open(lock_path, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with open(path, encoding="utf-8") as f:
            state = list(parse(f.read()))
        yield state
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)), prefix=".tasks-")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(render(*state))
        os.replace(tmp, path)          # atomic: readers never see a half-written file


def read(path: str):
    with open(path, encoding="utf-8") as f:
        return parse(f.read())


# ----------------------------------------------------------------------------- logic
def deps(row) -> list[str]:
    return [d.strip() for d in re.split(r"[,\s]+", row.get("requires", "")) if d.strip() and d.strip() != "-"]


def eligible(rows) -> list[dict]:
    status = {r["task_id"]: r["status"] for r in rows}
    return [r for r in rows if r["status"] == "open" and not r["owner"]
            and all(status.get(d) == "done" for d in deps(r))]


def find(rows, task_id):
    for r in rows:
        if r["task_id"] == task_id:
            return r
    raise LookupError(f"no task {task_id}")


def refuse(msg: str) -> int:
    print(f"REFUSED: {msg}", file=sys.stderr)
    return 1


def integrity_problems(rows, base_dir=".") -> list[str]:
    problems = []
    ids = [r["task_id"] for r in rows]
    for t in {i for i in ids if ids.count(i) > 1}:
        owners = sorted({r["owner"] for r in rows if r["task_id"] == t and r["owner"]})
        problems.append(f"COLLISION: {t} appears {ids.count(t)} times (owners: {', '.join(owners) or '-'})")
    for r in rows:
        t = r["task_id"]
        if r["status"] not in STATUSES:
            problems.append(f"{t}: unknown status '{r['status']}'")
        if re.search(r"[,/&]| and ", r["owner"]):
            problems.append(f"COLLISION: {t} has multiple owners '{r['owner']}'")
        if r["status"] in {"claimed", "done"} and not r["owner"]:
            problems.append(f"{t}: status {r['status']} but no owner")
        if r["status"] == "open" and r["owner"]:
            problems.append(f"{t}: open but owned by {r['owner']} (half-finished claim or release?)")
        for d in deps(r):
            if d not in ids:
                problems.append(f"{t}: requires unknown task {d}")
            elif r["status"] != "open" and find(rows, d)["status"] != "done":
                problems.append(f"{t}: is {r['status']} but dependency {d} is not done (ordering violated)")
        if r["status"] == "done" and r.get("artifact") and not os.path.exists(os.path.join(base_dir, r["artifact"])):
            problems.append(f"{t}: done but artifact {r['artifact']} does not exist")
    arts = [r["artifact"] for r in rows if r.get("artifact")]
    for a in {x for x in arts if arts.count(x) > 1}:
        problems.append(f"WRITE RACE RISK: artifact {a} is shared by several tasks")
    # dependency cycles
    graph = {r["task_id"]: deps(r) for r in rows}
    seen, stack = set(), set()

    def visit(n, path):
        if n in stack:
            problems.append("DEADLOCK: dependency cycle " + " -> ".join(path + [n]))
            return
        if n in seen or n not in graph:
            return
        seen.add(n); stack.add(n)
        for d in graph[n]:
            visit(d, path + [n])
        stack.discard(n)
    for n in graph:
        visit(n, [])
    return problems


# ----------------------------------------------------------------------------- commands
def main(argv: list[str]) -> int:
    path = "tasks.md"
    if "--file" in argv:
        i = argv.index("--file"); path = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    if not argv:
        print(__doc__); return 2
    cmd, args = argv[0], argv[1:]
    base = os.path.dirname(os.path.abspath(path))

    if cmd == "show":
        prefix, header, rows, suffix = read(path)
        print(render([], header, rows, []), end="")
        el = [r["task_id"] for r in eligible(rows)]
        print(f"\nclaimable now: {', '.join(el) or 'none'}")
        return 0
    if cmd == "next":
        el = eligible(read(path)[2])
        print(el[0]["task_id"] if el else "NONE")
        return 0
    if cmd == "check":
        rows = read(path)[2]
        problems = integrity_problems(rows, base)
        counts = {s: sum(r["status"] == s for r in rows) for s in STATUSES}
        print(f"{len(rows)} tasks: {counts['open']} open, {counts['claimed']} claimed, {counts['done']} done")
        for p in problems:
            print("  !", p)
        print("OK - no integrity problems" if not problems else f"{len(problems)} problem(s)")
        return 1 if problems else 0

    with locked(path) as state:
        rows = state[2]
        try:
            if cmd == "reset":
                for r in rows:
                    r["status"], r["owner"] = "open", ""
                print("all tasks reset to open")
                return 0
            if cmd == "claim-next":
                owner = args[0]
                el = eligible(rows)
                if not el:
                    print("NONE"); return 0
                el[0]["status"], el[0]["owner"] = "claimed", owner
                print(f"CLAIMED {el[0]['task_id']} -> write only to {el[0].get('artifact')}")
                return 0
            task_id, owner = args[0], args[1]
            r = find(rows, task_id)
            if cmd == "claim":
                if r["status"] != "open" or r["owner"]:
                    return refuse(f"{task_id} is {r['status']} (owner: {r['owner'] or '-'})")
                blocked = [d for d in deps(r) if find(rows, d)["status"] != "done"]
                if blocked:
                    return refuse(f"{task_id} requires {', '.join(blocked)} to be done first")
                r["status"], r["owner"] = "claimed", owner
                print(f"CLAIMED {task_id} -> write only to {r.get('artifact')}")
            elif cmd == "done":
                if r["owner"] != owner or r["status"] != "claimed":
                    return refuse(f"{task_id} is {r['status']} owned by {r['owner'] or '-'}, not claimed by {owner}")
                art = r.get("artifact")
                if art and (not os.path.exists(os.path.join(base, art)) or os.path.getsize(os.path.join(base, art)) == 0):
                    return refuse(f"artifact {art} missing or empty - write it before marking done")
                r["status"] = "done"
                print(f"DONE {task_id}")
            elif cmd == "release":
                if r["owner"] != owner:
                    return refuse(f"{task_id} is owned by {r['owner'] or 'nobody'}, not {owner}")
                r["status"], r["owner"] = "open", ""
                print(f"RELEASED {task_id}")
            else:
                print(__doc__); return 2
        except (LookupError, IndexError) as exc:
            return refuse(str(exc))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
