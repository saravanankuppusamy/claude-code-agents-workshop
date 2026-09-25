# Troubleshooting

Symptoms first, most common at the top.

## My hook never runs

1. **Folder not trusted.** Project agent hooks need the folder to be trusted. Launch
   `claude` interactively from the repo root once and accept the trust prompt. Headless
   `claude -p` in a never-trusted folder silently skips them. (Verified on 2.1.282.)
2. **YAML indentation / tabs.** Run `python3 tools/lint_agents.py path/to/.claude/agents`.
3. **Path doesn't resolve.** Relative paths resolve from where `claude` was launched.
   Use `python3 "${CLAUDE_PROJECT_DIR}/hooks/x.py"`.
4. **Wrong registration surface.** `TeammateIdle` must be in `.claude/settings.json`,
   never agent frontmatter. The linter flags it.
5. **`if:` too narrow.** A handler with `if: "Bash(sqlite3 *)"` is never spawned for
   other commands – by design. Don't put `if:` on security guards.
6. **Test it standalone:** `echo '<payload json>' | python3 hooks/x.py; echo $?`
7. Add a one-line payload logger at the top of the script (see `module-4-agent-teams/demo-15-quality-gates/hooks/gates_common.py`).

## My hook runs but doesn't block

- Exit code must be **2** (or exit 0 + JSON `permissionDecision: "deny"`). Exit 1 is a
  non-blocking error.
- JSON is ignored on exit 2 – pick one style.
- JSON must be under `hookSpecificOutput` with `"hookEventName": "PreToolUse"`.
- It's a `PostToolUse` hook – those can't block; the tool already ran.

## My subagent ignores my edits

- A same-name agent at a higher scope wins (session › project › user › plugin). Check
  `~/.claude/agents/` and whether you launched with `--agents`.
- Agents and skills load at session start. Exit and relaunch after editing.
- YAML error → file silently skipped. Lint it.

## "Read-only" agent modified a file

It had Bash (or a denylist that forgot Bash/NotebookEdit). Use an allowlist; see demo 03.

## I asked for a team and got subagents

- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` isn't `1` in this session – run
  `module-4-agent-teams/demo-13-first-team/check-teams-ready.sh`.
- Say explicitly "Create an agent team".
- `claude -p` never spawns teammates (interactive only).

## No split panes

Need tmux (or iTerm2 + `it2`), started *before* `claude`, and `teammateMode` `auto`/`tmux`
or `--teammate-mode tmux`. VS Code's integrated terminal doesn't support split panes –
use in-process mode (↑/↓ + Enter in the agent panel).

## Teammates keep asking permission

Prompts from teammates surface in the lead. Pre-approve with `permissions.allow` in
`.claude/settings.json` (see demos 13–17). Avoid `--dangerously-skip-permissions`
outside a disposable environment.

## A teammate never goes idle / bounces forever

A gate that can never pass. Run the gate's tests with a known-good artifact
(`demo-15 tests/test_gates.py::test_golden_artifact_passes_every_completion_gate`) and
check `hooks/gate-log.jsonl` for the repeated reason.

## Orphaned tmux sessions after a team run

```bash
tmux ls
tmux kill-session -t <name>
```

## Reset a demo

Most demos ship `./reset.sh`. Demo 04 installs a **user-scope** agent – always run
`./scope-demo.sh remove-user` afterwards.
