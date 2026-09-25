# After-class practice path

Work through in order; each level assumes the previous. ⏱ = rough time. Every item
points at the demo whose files you can copy from.

## Level 1 – Solid subagents (≈ 2 h)

| ✓ | Exercise | ⏱ | Start from |
|---|---|---|---|
| ☐ | Write `context-probe-strict` (Read only, `omitClaudeMd: true`); predict its report, then run it | 15 m | demo 01 |
| ☐ | Ask Claude to generate an agent from a prompt; diff it against a hand-written one; list what was missing | 15 m | demo 02 |
| ☐ | Run the linter on your own `~/.claude/agents`; fix every warning | 15 m | `tools/lint_agents.py` |
| ☐ | Build a same-name project/user pair for your own domain; prove precedence from inside and outside the project | 20 m | demo 04 |
| ☐ | Fill `worksheet.md` for three agents from your real work; validate one model change against an answer key | 30 m | demo 05 |
| ☐ | Give a reviewer Bash, then write a PreToolUse hook that blocks `sed -i`, `>`, `tee`, `mv` | 25 m | demos 03 + 09 |

## Level 2 – Controlled, stateful agents (≈ 3 h)

| ✓ | Exercise | ⏱ | Start from |
|---|---|---|---|
| ☐ | Extend `restrict_writes.py` to catch Bash redirections outside `out/`; add a symlink test | 30 m | demo 06 |
| ☐ | Add `schema_version` to the state template and a v1→v2 migration in `validate_state.py` | 30 m | demo 07 |
| ☐ | Add a `PreCompact` hook that snapshots the state file | 15 m | demo 07 |
| ☐ | Write a skill for your team's conventions, bundle a checker script, preload it into two agents | 40 m | demo 08 |
| ☐ | Break `sql_guard.py` with a new test case, then fix it | 30 m | demo 09 |
| ☐ | Add `deny_columns` to the SQL policy | 20 m | demo 09 |
| ☐ | Make the background indexer resumable from `files_done` | 30 m | demo 10 |

## Level 3 – Multi-agent workflows (≈ 3 h)

| ✓ | Exercise | ⏱ | Start from |
|---|---|---|---|
| ☐ | Add a count check between pipeline stages in `run-pipeline.sh` | 15 m | demo 11 |
| ☐ | Add a parallel branch (`owner-notifier`) to the chain – and explain why it's no longer a chain | 30 m | demo 11 |
| ☐ | Convert the generic researcher into three hypothesis-specific agents plus a shared skill | 30 m | demo 12 |
| ☐ | Add `priority` and stale-claim detection to `tasklist.py` | 40 m | demo 14 |
| ☐ | Point the TeammateIdle gate at demo 14's `tasks.md` and run that team | 30 m | demos 14 + 15 |
| ☐ | Add a fourth teammate to `/release-check` by editing only the skill + one agent file | 20 m | demo 16 |
| ☐ | Fix BUG-212 so all four reproducer rows read 0/10; add the escalation protocol | 45 m | demo 17 |

## Capstone (half a day)

Pick a real, recurring task from your own work that has at least two independent
parts. Build it end to end:

1. Decide the tier with the question: *does anyone need to redirect anyone during the run?*
2. Agent definitions with allowlists, models, `maxTurns` – lint clean.
3. At least one PreToolUse guard with tests (golden good case + known bad cases).
4. If a team: a spawn-prompt skill with named agents, checkable gates, stop conditions;
   TeammateIdle/TaskCompleted gates with a golden-artifact test.
5. A README using the demo template: Why · Files · Run it · What to observe · Practice.

Share it with your cohort – the best capstones become new demos.
