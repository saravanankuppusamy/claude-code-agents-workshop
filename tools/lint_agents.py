#!/usr/bin/env python3
"""
lint_agents.py - catch the silent failures in subagent definition files.

The course repeatedly warns that frontmatter mistakes fail *silently*: a tab in the
YAML, a misspelled tool name, a denylist that forgot a write-capable tool, a hook
script path that does not resolve. This linter makes those mistakes loud.

Usage:
    python3 tools/lint_agents.py path/to/.claude/agents            # a directory
    python3 tools/lint_agents.py path/to/agent.md other-agent.md    # specific files
    python3 tools/lint_agents.py --all                              # every agent in this repo

Exit code: 0 = no errors (warnings allowed), 1 = at least one error.

Works with the standard library only. If PyYAML is installed it is used for a
stricter parse; otherwise a small built-in parser handles the subset used by
agent files (scalars, folded descriptions, simple lists, nested hook blocks).
"""
from __future__ import annotations

import os
import re
import shlex
import sys
from pathlib import Path

try:  # optional stricter parsing
    import yaml  # type: ignore
except Exception:  # pragma: no cover - PyYAML not installed
    yaml = None

KNOWN_FIELDS = {
    "name", "description", "tools", "disallowedTools", "model", "permissionMode",
    "maxTurns", "skills", "mcpServers", "hooks", "memory", "background", "effort",
    "isolation", "color", "initialPrompt", "omitClaudeMd", "experimental",
}
KNOWN_TOOLS = {
    "Agent", "Task", "AskUserQuestion", "Bash", "CronCreate", "CronDelete", "CronList",
    "Edit", "MultiEdit", "EnterPlanMode", "ExitPlanMode", "EnterWorktree", "ExitWorktree",
    "Glob", "Grep", "ListMcpResourcesTool", "ReadMcpResourceTool", "NotebookEdit",
    "Read", "Skill", "TaskCreate", "TaskGet", "TaskList", "TaskOutput", "TaskStop",
    "TaskUpdate", "ToolSearch", "WebFetch", "WebSearch", "Write", "SendMessage",
    "Monitor", "LSP", "TodoWrite",
}
WRITE_CAPABLE = ["Write", "Edit", "MultiEdit", "NotebookEdit", "Bash"]
MODEL_ALIASES = {"haiku", "sonnet", "opus", "fable", "inherit"}
PERMISSION_MODES = {"default", "acceptEdits", "auto", "dontAsk", "bypassPermissions", "plan", "manual"}
MEMORY_SCOPES = {"user", "project", "local"}
EFFORT_LEVELS = {"low", "medium", "high", "xhigh", "max"}


class Report:
    def __init__(self, path: Path):
        self.path = path
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def error(self, msg): self.errors.append(msg)
    def warn(self, msg): self.warnings.append(msg)
    def note(self, msg): self.notes.append(msg)


# --------------------------------------------------------------------------- parsing
def split_frontmatter(text: str):
    if not text.startswith("---"):
        return None, text
    lines = text.splitlines()
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:])
    return None, text


def mini_yaml(fm: str) -> dict:
    """Parse the subset of YAML used in agent frontmatter (no PyYAML needed)."""
    data: dict = {}
    key = None
    block: list[str] = []

    def flush():
        if key is None:
            return
        raw = data.get(key)
        if raw == "" and block:
            items = [b.strip() for b in block if b.strip()]
            if items and all(i.startswith("- ") or i == "-" for i in items) and \
                    all(not b.startswith("    ") for b in block if b.strip()):
                data[key] = [i[2:].strip() for i in items]
            else:
                data[key] = {"__raw__": "\n".join(block)}
        elif block:  # folded continuation of a scalar
            data[key] = (raw + " " + " ".join(b.strip() for b in block)).strip()

    for line in fm.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m and not line.startswith((" ", "-")):
            flush()
            key, val = m.group(1), m.group(2).strip()
            data[key] = val.strip('"').strip("'")
            block = []
        else:
            block.append(line)
    flush()
    return data


def parse(fm: str, rep: Report) -> dict:
    if yaml is not None:
        try:
            parsed = yaml.safe_load(fm) or {}
            if isinstance(parsed, dict):
                return parsed
            rep.error("frontmatter did not parse to a mapping")
            return {}
        except Exception as exc:  # YAML error = silent failure in Claude Code
            rep.error(f"YAML parse error (Claude Code may silently ignore this file): {exc}")
            return mini_yaml(fm)
    return mini_yaml(fm)


def as_list(value) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [t.strip() for t in str(value).split(",") if t.strip()]


# --------------------------------------------------------------------------- checks
def check_tool_names(names, field, rep):
    for t in names:
        base = t.split("(")[0]
        if base.startswith("mcp__"):
            if not re.match(r"^mcp__[\w.-]+(__[\w.*-]+)?$", base):
                rep.warn(f"{field}: '{t}' does not match mcp__<server>__<tool>")
            else:
                rep.note(f"{field}: MCP tool '{t}' is only honoured if that server is running")
        elif base not in KNOWN_TOOLS and base.lower() in {k.lower() for k in KNOWN_TOOLS}:
            canon = next(k for k in KNOWN_TOOLS if k.lower() == base.lower())
            rep.warn(f"{field}: '{t}' - case differs from the registered name '{canon}'. "
                     f"Claude Code tolerates some variations, but copy names verbatim.")
        elif base not in KNOWN_TOOLS:
            rep.warn(f"{field}: '{t}' is not a known built-in tool name - unknown names are "
                     f"silently dropped. Check spelling against /tools.")
        if base == "MultiEdit":
            rep.note(f"{field}: MultiEdit is a legacy name; harmless, but confirm it exists in your version")


def check_hooks(hooks, agent_path: Path, rep):
    text = hooks.get("__raw__", "") if isinstance(hooks, dict) and "__raw__" in hooks else str(hooks)
    if "\t" in text:
        rep.error("hooks block contains a TAB - hooks will silently not register")
    commands = re.findall(r"command['\"]?:\s*['\"]?([^'\"\n}]+)", text)
    project_root = agent_path.parent.parent.parent  # <root>/.claude/agents/x.md
    for cmd in commands:
        try:
            parts = shlex.split(cmd)
        except ValueError:
            parts = cmd.split()
        scripts = [p for p in parts if p.endswith((".py", ".sh"))]
        for s in scripts:
            s_resolved = s.replace("${CLAUDE_PROJECT_DIR}", str(project_root)) \
                          .replace("$CLAUDE_PROJECT_DIR", str(project_root))
            p = Path(s_resolved)
            if not p.is_absolute():
                p = project_root / p
            if not p.exists():
                rep.error(f"hook script not found: {s} (resolved to {p}). Hook paths resolve "
                          f"from the directory Claude Code is launched in - use ${{CLAUDE_PROJECT_DIR}}.")
            elif parts and parts[0] == s and not os.access(p, os.X_OK):
                rep.error(f"hook script {s} is invoked directly but is not executable (chmod +x)")
    if isinstance(hooks, dict):
        for event in hooks:
            if event == "TeammateIdle":
                rep.error("TeammateIdle registered in agent frontmatter - it must live in "
                          ".claude/settings.json (team coordination layer)")


def lint_file(path: Path) -> Report:
    rep = Report(path)
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    if fm is None:
        rep.error("no YAML frontmatter found (file must start with --- and have a closing ---)")
        return rep
    if "\t" in fm:
        rep.error("frontmatter contains TAB characters - use spaces only")
    data = parse(fm, rep)

    for k in data:
        if k not in KNOWN_FIELDS:
            rep.warn(f"unknown frontmatter field '{k}' (typo? unknown fields are ignored)")

    name = str(data.get("name", "")).strip()
    if not name:
        rep.error("missing required field: name")
    elif not re.match(r"^[a-z0-9][a-z0-9-]*$", name):
        rep.warn(f"name '{name}' - convention is lowercase-with-hyphens")
    if name and path.stem != name:
        rep.note(f"file name '{path.stem}' differs from name '{name}' (allowed, but confusing)")
    if not str(data.get("description", "")).strip():
        rep.error("missing required field: description (the orchestrator uses it to pick agents)")

    model = str(data.get("model", "")).strip()
    if model:
        if model.lower() in MODEL_ALIASES:
            if model != model.lower():
                rep.note(f"model '{model}': docs use lowercase aliases ('{model.lower()}')")
        elif not model.startswith("claude-") and "/" not in model:
            rep.warn(f"model '{model}' is not a known alias or full model id")
    else:
        rep.note("no model set - the subagent inherits the parent's model")

    if "maxTurns" not in data:
        rep.warn("no maxTurns - add a circuit breaker to bound cost and runaway loops")
    else:
        try:
            if int(data["maxTurns"]) <= 0:
                rep.error("maxTurns must be a positive integer")
        except (TypeError, ValueError):
            rep.error(f"maxTurns '{data['maxTurns']}' is not an integer")

    pm = str(data.get("permissionMode", "")).strip()
    if pm:
        if pm not in PERMISSION_MODES:
            rep.error(f"permissionMode '{pm}' is not valid ({', '.join(sorted(PERMISSION_MODES))})")
        if pm == "bypassPermissions":
            rep.warn("permissionMode bypassPermissions - hooks are now your ONLY control layer")
        if pm == "dontAsk" and "tools" not in data:
            rep.warn("dontAsk without a tools allowlist - pair dontAsk with a narrow tools list")

    mem = str(data.get("memory", "")).strip()
    if mem and mem not in MEMORY_SCOPES:
        rep.error(f"memory '{mem}' must be one of user, project, local")
    eff = str(data.get("effort", "")).strip()
    if eff and eff not in EFFORT_LEVELS:
        rep.error(f"effort '{eff}' must be one of {', '.join(sorted(EFFORT_LEVELS))}")

    tools = as_list(data.get("tools"))
    denied = as_list(data.get("disallowedTools"))
    check_tool_names(tools, "tools", rep)
    check_tool_names(denied, "disallowedTools", rep)

    if not tools and denied:
        base_denied = {d.split("(")[0] for d in denied}
        leaks = [t for t in WRITE_CAPABLE if t not in base_denied]
        rep.warn("denylist-only agent: every tool NOT listed stays available. "
                 f"Write-capable tools still reachable: {', '.join(leaks) or 'none'}")
    if not tools and not denied:
        rep.warn("no tools and no disallowedTools - agent inherits EVERY available tool")
    if tools:
        base_tools = {t.split("(")[0] for t in tools}
        for d in denied:
            if d.split("(")[0] not in base_tools:
                rep.note(f"disallowedTools '{d}' has no extra effect - it is not in the allowlist anyway")
        desc = str(data.get("description", "")).lower() + body.lower()
        if "read-only" in desc or "read only" in desc or "never modif" in desc:
            writers = [t for t in WRITE_CAPABLE if t in base_tools]
            if writers:
                rep.warn(f"agent describes itself as read-only but can call {', '.join(writers)} "
                         f"(Bash can write files with sed -i, >, tee...)")

    skills = as_list(data.get("skills"))
    project_root = path.parent.parent.parent
    for s in skills:
        if "/" in s or s.endswith(".md"):
            rep.warn(f"skills entry '{s}' looks like a path - current Claude Code expects skill "
                     f"NAMES (e.g. 'code-style' for .claude/skills/code-style/SKILL.md)")
        else:
            candidates = [project_root / ".claude" / "skills" / s / "SKILL.md",
                          Path.home() / ".claude" / "skills" / s / "SKILL.md"]
            if not any(c.exists() for c in candidates):
                rep.warn(f"skill '{s}' not found in project or user skills (it will be skipped)")

    if "hooks" in data:
        check_hooks(data["hooks"], path, rep)
    if not body.strip():
        rep.warn("empty system prompt body")
    return rep


# --------------------------------------------------------------------------- main
def collect(args: list[str]) -> list[Path]:
    if args == ["--all"]:
        root = Path(__file__).resolve().parent.parent
        return sorted(p for p in root.rglob(".claude/agents/*.md"))
    files: list[Path] = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            files += sorted(p.glob("*.md"))
        elif p.exists():
            files.append(p)
        else:
            print(f"not found: {a}", file=sys.stderr)
    return files


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    files = collect(argv)
    if not files:
        print("no agent files found")
        return 1
    total_err = 0
    for f in files:
        rep = lint_file(f)
        status = "FAIL" if rep.errors else ("WARN" if rep.warnings else "OK  ")
        print(f"[{status}] {f}")
        for m in rep.errors:
            print(f"    ERROR   {m}")
        for m in rep.warnings:
            print(f"    warning {m}")
        for m in rep.notes:
            print(f"    note    {m}")
        total_err += len(rep.errors)
    print(f"\n{len(files)} file(s) checked, {total_err} error(s)")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
