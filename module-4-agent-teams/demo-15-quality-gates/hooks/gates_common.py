"""Shared helpers for the team quality-gate hooks.

Design choices worth teaching:
  * Every invocation is logged WITH ITS FULL PAYLOAD (hooks/gate-log.jsonl). Payload
    field names differ between the lesson, the docs and releases - log first, then code.
  * Liveness gates (TeammateIdle) fail OPEN on unknown input: blocking idle forever on
    a payload you can't parse hangs the team. Security gates fail CLOSED (demo 09).
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def load_config():
    with open(os.path.join(ROOT, "gates.json"), encoding="utf-8") as f:
        return json.load(f)


def read_payload():
    try:
        return json.load(sys.stdin)
    except ValueError:
        return {}


def log(cfg, event, payload, decision, reason=""):
    path = os.path.join(ROOT, cfg.get("log_file", "hooks/gate-log.jsonl"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                            "event": event, "decision": decision, "reason": reason,
                            "payload": payload}) + "\n")


def teammate_name(payload):
    """Best-effort identity. Order: explicit names first, agent_type last (it is the
    *definition* name and may be shared by several teammates)."""
    for key in ("teammate_name", "teammate", "agent_name", "name"):
        if payload.get(key):
            return str(payload[key])
    if payload.get("agent_id"):
        return str(payload["agent_id"]).split("@")[0]
    return payload.get("agent_type")


def validate_artifact(cfg, rel_path):
    """Return a list of problems with a findings artifact (empty list = good)."""
    path = os.path.join(ROOT, rel_path)
    if not os.path.exists(path):
        return [f"{rel_path} does not exist"]
    text = open(path, encoding="utf-8").read()
    if not text.strip():
        return [f"{rel_path} is empty"]
    problems = [f"missing section '{s}'" for s in cfg["required_sections"] if s not in text]
    if "## Findings" in text:
        body = text.split("## Findings", 1)[1].split("\n## ", 1)[0]
        n = len(re.findall(r"(?m)^\s*(?:[-*]|\d+\.)\s+\S", body))
        if n < cfg.get("min_findings", 1):
            problems.append(f"'## Findings' has {n} item(s); need at least {cfg['min_findings']} "
                            f"(or write '- None found' with the files you checked)")
    return [f"{rel_path}: {p}" if not p.startswith(rel_path) else p for p in problems]
