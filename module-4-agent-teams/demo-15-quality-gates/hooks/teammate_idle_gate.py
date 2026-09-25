#!/usr/bin/env python3
"""TeammateIdle gate (register in .claude/settings.json - NOT in agent frontmatter).

exit 0 -> teammate may go idle
exit 2 -> teammate keeps working; stdout/stderr text is its feedback

Two modes, chosen automatically:
  A. tasks.md present (hand-authored list, demo 14 / Lab 6 style)
       - teammate still has a CLAIMED task      -> block: finish it
       - eligible OPEN tasks remain              -> block: claim the next one (queue drain)
       - teammate's DONE tasks have bad artifacts -> block: fix them
  B. no tasks.md (platform-managed list)
       - validate the convention artifact findings/<name>.md
Phase awareness (Lesson 4.8.3.2.1): a teammate with no claimed/done work yet (plan
phase) is allowed to idle.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gates_common as g  # noqa: E402


def decide(cfg, payload):
    name = g.teammate_name(payload)
    if not name:
        return 0, "unrecognised payload - allowing idle (liveness gates fail open)"
    tasks_path = os.path.join(g.ROOT, cfg.get("tasks_file", "tasks.md"))
    if os.path.exists(tasks_path):
        rows = _rows(tasks_path)
        mine = [r for r in rows if r.get("owner") == name]
        claimed = [r["task_id"] for r in mine if r["status"] == "claimed"]
        if claimed:
            return 2, f"{name}: you still own claimed task(s) {', '.join(claimed)}. Finish and mark them done."
        problems = [p for r in mine if r["status"] == "done" and r.get("artifact")
                    for p in g.validate_artifact(cfg, r["artifact"])]
        if problems:
            return 2, "Fix before stopping: " + "; ".join(problems)
        status = {r["task_id"]: r["status"] for r in rows}
        eligible = [r["task_id"] for r in rows if r["status"] == "open" and not r.get("owner")
                    and all(status.get(d.strip()) == "done"
                            for d in r.get("requires", "").replace(",", " ").split() if d.strip())]
        if eligible:
            return 2, f"{len(eligible)} eligible task(s) still open ({', '.join(eligible)}). Claim the next one."
        return 0, f"{name}: queue drained and artifacts valid"
    artifact = cfg["artifact_pattern"].format(name=name)
    if not os.path.exists(os.path.join(g.ROOT, artifact)):
        return 0, f"{name}: no {artifact} yet - treating as plan phase, idle allowed"
    problems = g.validate_artifact(cfg, artifact)
    if problems:
        return 2, "Fix before stopping: " + "; ".join(problems)
    return 0, f"{name}: {artifact} valid"


def _rows(path):
    import re
    rows, header = [], None
    for line in open(path, encoding="utf-8"):
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower().replace(" ", "_") for c in cells]
        elif not re.match(r"^-+$", cells[0]):
            rows.append(dict(zip(header, cells + [""] * (len(header) - len(cells)))))
    return rows


if __name__ == "__main__":
    cfg = g.load_config()
    payload = g.read_payload()
    code, reason = decide(cfg, payload)
    g.log(cfg, "TeammateIdle", payload, "block" if code == 2 else "allow", reason)
    if code == 2:
        print(reason, file=sys.stderr)
    sys.exit(code)
