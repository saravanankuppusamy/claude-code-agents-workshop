# Cheat sheet – subagents, hooks and agent teams

## Subagent file (`.claude/agents/<name>.md`)

```markdown
---
name: log-triage                # required, lowercase-hyphens
description: <when to use it>   # required – written for the orchestrator
model: haiku                    # haiku | sonnet | opus | fable | inherit | full id
effort: medium                  # low | medium | high | xhigh | max
maxTurns: 10                    # circuit breaker
tools: Read, Grep, Glob         # ALLOWLIST (preferred)
disallowedTools: WebFetch       # denylist – removes from inherited/allowed set
permissionMode: default         # default | acceptEdits | auto | dontAsk | bypassPermissions | plan
skills:                         # skill NAMES -> .claude/skills/<name>/SKILL.md
  - team-style
memory: project                 # user | project | local  (platform-managed memory)
background: false               # true = always run in background
isolation: worktree             # run in a throwaway git worktree
color: cyan
hooks:
  PreToolUse:
  - matcher: Bash
    hooks:
    - type: command
      command: python3 "${CLAUDE_PROJECT_DIR}/hooks/guard.py"
---
System prompt: role, procedure, exact output format.
```

Lint: `python3 tools/lint_agents.py .claude/agents`

Sizing `maxTurns`: see [choosing-maxturns.md](choosing-maxturns.md).

## Scopes (highest wins on name collision)

managed settings › `--agents '{json}'` (session) › `.claude/agents/` (project) ›
`~/.claude/agents/` (user) › plugin `agents/` (no hooks / permissionMode / mcpServers)

`--agent <name>` runs the *main session* as that agent – it creates no scope.

## What crosses into a subagent

| Crosses | Doesn't |
|---|---|
| the `prompt` string · its own system prompt · CLAUDE.md (default) · env vars · cwd · session permission limits (narrow only) | parent conversation · parent tool results · anything you didn't write into `prompt` |

Only the subagent's **final message** returns to the parent.

## Models

| Alias | Use for |
|---|---|
| haiku | scanning, extraction, formatting, high-volume deterministic work |
| sonnet | review, multi-step reasoning, clustering, most code generation |
| opus | high-stakes review, complex analysis |
| fable | longest-horizon autonomous work, deep research |

Resolution: per-call `model` › frontmatter `model` › `CLAUDE_CODE_SUBAGENT_MODEL` › parent.

## Permission modes

| Mode | Behaviour | Failure to expect |
|---|---|---|
| default | prompts before edits and shell | slow |
| acceptEdits | edits auto-approved; shell prompts | silent overwrites if paths are wrong |
| auto | classifier approves routine, blocks risky | classifier can approve something undesirable |
| dontAsk | only pre-approved calls run; others denied, no prompt | "no prompts" ≠ "can do everything" |
| plan | explore/plan; edits blocked | approved shell commands may still run |
| bypassPermissions | no checks | hooks are your only control |

## Hooks – exit codes

| Event | exit 0 | exit 2 | JSON (exit 0) |
|---|---|---|---|
| PreToolUse | allow | block, stderr → model | `hookSpecificOutput.permissionDecision`: allow / deny (+ `permissionDecisionReason`, `updatedInput`) |
| PostToolUse | observe | not blocking | `additionalContext` |
| SubagentStop / Stop | stop | keep going, stderr → agent | – (guard with `stop_hook_active`) |
| TeammateIdle | go idle | keep working, stderr = feedback | `{"continue": false}` stops the teammate |
| TaskCreated | create | reject | – |
| TaskCompleted | complete | refuse | – |

Any other non-zero exit = non-blocking error. Never mix JSON with exit 2.

Where to register: PreToolUse/PostToolUse/Stop → agent frontmatter or settings ·
TaskCreated/TaskCompleted → settings (works for all) · **TeammateIdle → settings only**.

Test without Claude:
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | python3 hooks/guard.py; echo $?
```

## Agent teams

```json
// ~/.claude/settings.json
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" }, "teammateMode": "in-process" }
```

| Mode | Launch |
|---|---|
| in-process (default) | ↑/↓ select teammate · Enter view/message · Esc back · Ctrl+T task list · x stop |
| auto / tmux / iterm2 | `claude --teammate-mode tmux` (inside tmux) |

Spawn prompt = **agents** (named, typed) + **gates** (checkable conditions) + **stop
conditions**. Store it as `.claude/skills/<workflow>/SKILL.md` with
`disable-model-invocation: true`.

State on disk: `~/.claude/teams/<team>/config.json` (don't edit) ·
`~/.claude/tasks/<team>/` (platform task list).

## Tier decision

Does anyone need to redirect anyone **during** the run?
No → parallel subagents (or one). Yes → agent team. Sequential → chain or single agent.
