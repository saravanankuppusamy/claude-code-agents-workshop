# Version notes: course text vs. current docs vs. observed behaviour

The WA3877 v1.5.0 guides are accurate on concepts. A few mechanics have moved in current
Claude Code. The demos follow **current documentation**, and several items were verified
by running them on **Claude Code 2.1.282** (September 2026). Where they differ, trust what
you observe on the version in front of you and tell the class which version you ran.

| # | Topic | Course says | Current docs / observed | Where it matters |
|---|---|---|---|---|
| 1 | `skills:` frontmatter | list of **file paths** (`- .claude/skills/code-style.md`) | list of **skill names** resolving to `.claude/skills/<name>/SKILL.md`. **Verified:** the skill is injected as the 2nd message of the subagent transcript | Lab 3, demo 08 |
| 2 | Subagents and CLAUDE.md | CLAUDE.md influences subagents mainly via the orchestrator | Subagents load CLAUDE.md by default (`omitClaudeMd: true` turns it off). **Verified** with demo 01's probe | Lab 2, demo 01 |
| 3 | Model aliases | `Haiku`, `Sonnet`, `Opus` (capitalised) | docs use lowercase `haiku`, `sonnet`, `opus`, `fable`, `inherit` | all labs – both appear to work; demos use lowercase |
| 4 | Hook folder trust | not mentioned | Project-level agent hooks require the folder to be **trusted**. **Verified:** in an untrusted folder, frontmatter hooks silently didn't run. Trust is keyed to the **git repo root** when demos are inside a clone | Lab 4, every hook demo – see troubleshooting |
| 5 | PreToolUse JSON output | top-level `permissionDecision` | nested: `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}`. **Verified** deny works, including under `--dangerously-skip-permissions` | Lab 4, demo 09 |
| 6 | PostToolUse result field | `tool_response` with `output` | **Verified:** `tool_response` is an object: `{"stdout", "stderr", "interrupted", ...}` for Bash | demo 09 `audit_log.py` reads it defensively |
| 7 | PostToolUse stdout | "stdout replaces the tool output the model sees" | docs describe `additionalContext` in `hookSpecificOutput` for feeding text back | demo 09 practice item |
| 8 | Hook payload `effort` | present in PreToolUse/PostToolUse | not present in our 2.1.282 test payloads (docs list it) | don't depend on it |
| 9 | `if:` on hooks | at the matcher level | on the individual hook handler (`hooks: - type: command / if: ...`). **Verified** handler-level `if` on PostToolUse | Lab 4 Ch. 3, demo 09 |
| 10 | Multiple hooks per event | run in list order, first non-zero stops the chain | docs describe matching hooks running in parallel; design each hook to be independent | demo 09 |
| 11 | TeammateIdle payload | `teammate_name`, `team_name` | docs: `agent_type`, `agent_id` (+ common fields) | Lab 6 `validate-findings.py` – demo 15 resolves identity from several keys and logs full payloads |
| 12 | TaskCompleted payload | `task_id`, `owner`, `artifact`, `status` | docs: `task_id`, `task_title`, `result`. Fires for the **platform** task list (TaskCreate/TaskUpdate), not for a hand-edited `tasks.md` | demo 15 puts the artifact path in the task title |
| 13 | TaskCompleted registration | lead agent frontmatter | settings.json works for all agents; demo 15 uses settings | demo 15 |
| 14 | SubagentStop payload | – | **Verified** fields: `agent_id`, `agent_type`, `agent_transcript_path`, `stop_hook_active`, `last_assistant_message` | demo 07 |
| 15 | Broadcast | `SendMessage(to="all")` | docs: "To reach everyone, send one message per recipient" | demo 13 prompt C |
| 16 | Plan approval | a system-prompt convention (Lab 6) | also a platform feature: teammates spawned while the lead is in plan mode send plan-approval requests; the lead approves automatically | demo 13 practice |
| 17 | Scope precedence | session › project › user › plugin | **managed settings** sit above session scope; nested `.claude/agents/` closest to the cwd wins | demo 04 |
| 18 | Team size guidance | 2–4 teammates | docs suggest 3–5 for most workflows, 5–6 tasks per teammate | Lesson 4.9 discussion |
| 19 | Teammate `skills` | – | a subagent definition's `skills` are **not** applied when used as a teammate type | Module 4 |
| 20 | Teammate permissions | – | teammates inherit the lead's mode, **except `dontAsk`**; `--dangerously-skip-permissions` on the lead applies to all | Lab 6 |
| 21 | `MultiEdit` | listed as a tool | may not exist in your version; harmless in lists. The bigger denylist leak is **Bash** | Lab 1, demo 03 |
| 22 | Background default | "subagents run in the background by default" | docs: in fork mode (interactive default) spawned subagents run in background; `background: true` forces it | demo 10 |
| 23 | `--max-turns` CLI flag | – | not listed in `claude --help` on 2.1.282; use `maxTurns` in frontmatter | demo 11 script |

## How to check quickly on your version

```bash
claude --version
claude --help | grep -E -- "--agent|--agents|--permission-mode|--allowedTools"
# Capture real hook payloads: add a logging hook (demo 15's gates log every payload)
```
