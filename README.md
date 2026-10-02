# Claude Code Agents Workshop – demos & practice

Companion repository for **WA3877 – Advanced Claude Code with Agents** (1-day course):
17 runnable demos that make each lesson concept visible, reference solutions for the
lab challenges, and a self-paced practice path for after class.

Every demo is a self-contained Claude Code project: `cd` into it and run `claude`.
All helper scripts are Python standard library only, and every hook ships with tests
you can run without Claude.

```
.
├── module-2-subagents/          Lesson 2 · Labs 1–2   demos 01–05
├── module-3-advanced-patterns/  Lesson 3 · Labs 3–4   demos 06–12
├── module-4-agent-teams/        Lesson 4 · Labs 5–6   demos 13–17
├── tools/lint_agents.py         catches silent frontmatter failures
├── docs/
│   ├── cheatsheet.md            one-page reference
│   ├── choosing-maxturns.md     how to size the maxTurns circuit breaker
│   ├── after-class-practice.md  self-paced path with difficulty levels
│   ├── version-notes.md         course text vs current Claude Code
│   └── troubleshooting.md
├── INSTRUCTOR-GUIDE.md          run of show, timings, what goes wrong live
└── run-tests.sh                 all offline tests (also runs in GitHub Actions)
```

## Prerequisites

- Claude Code (tested with **2.1.282**) and an authenticated account
- Python 3.10+ (standard library only), `git`, `sqlite3` CLI (demo 09)
- For agent-team demos: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; `tmux` for split panes (optional)

## Quick start

```bash
git clone <this-repo> claude-code-agents-workshop
cd claude-code-agents-workshop
./run-tests.sh                 # offline checks – should print ALL CHECKS PASSED
claude                         # once, from the repo root: accept the folder-trust prompt
```

> **Accept folder trust once from the repo root.** Hooks defined in project agents do
> not run in an untrusted folder – and nothing tells you. See `docs/troubleshooting.md`.

Then pick a demo and follow its README, e.g.:

```bash
cd module-3-advanced-patterns/demo-09-hooks-guard-and-audit
./reset.sh
claude
```

## Demo map

| # | Demo | Lesson | Lab | You will see |
|---|---|---|---|---|
| 01 | [Context isolation](module-2-subagents/demo-01-context-isolation/) | 2.2 | – | what crosses the parent → subagent boundary, proven by a probe agent |
| 02 | [Built-in vs custom](module-2-subagents/demo-02-builtin-vs-custom/) | 2.3 | – | Explore/Plan vs a custom agent with an output contract |
| 03 | [Allowlist vs denylist](module-2-subagents/demo-03-allowlist-vs-denylist/) | 2.6–2.7 | 1 | a "read-only" agent editing a file via Bash; the linter |
| 04 | [Scope precedence](module-2-subagents/demo-04-scope-precedence/) | 2.5 | 2 | session › project › user; `--agents` vs `--agent` |
| 05 | [Model selection](module-2-subagents/demo-05-model-selection/) | 2.8 | 2 | Haiku/Sonnet/Opus against an answer key |
| 06 | [Permission modes & control stack](module-3-advanced-patterns/demo-06-permission-modes/) | 3.3 | – | four layers protecting a PII export |
| 07 | [Memory & state](module-3-advanced-patterns/demo-07-memory-and-state/) | 3.4 | 3 | `memory:` vs state file; schema, validator, pruning, SubagentStop gate |
| 08 | [Skills preload](module-3-advanced-patterns/demo-08-skills-preload/) | 3.5 | 3 | one skill file, two agents; skills with scripts |
| 09 | [Hooks: guard & audit](module-3-advanced-patterns/demo-09-hooks-guard-and-audit/) | 3.6–3.7 | 4 | naive vs robust guard, `updatedInput`, audit log, rate limit |
| 10 | [Background agents](module-3-advanced-patterns/demo-10-background-agents/) | 3.8 | – | manifest, heartbeat, idempotency, output validation |
| 11 | [Chaining pipeline](module-3-advanced-patterns/demo-11-chaining-pipeline/) | 3.9 | – | JSON contracts between stages; `claude -p` pipeline |
| 12 | [Parallel & noisy](module-3-advanced-patterns/demo-12-parallel-and-noisy/) | 3.9–3.10 | 5 | fan-out research; 2,000 lines kept out of context |
| 13 | [First team](module-4-agent-teams/demo-13-first-team/) | 4.2–4.5 | 5 | pre-flight, research team, steering teammates |
| 14 | [Hand-authored task list](module-4-agent-teams/demo-14-hand-authored-tasklist/) | 4.4–4.6 | 6 | the claim race, and a locked claim tool that prevents it |
| 15 | [Quality gates](module-4-agent-teams/demo-15-quality-gates/) | 4.8 | 6 | TeammateIdle / TaskCreated / TaskCompleted with tests |
| 16 | [Spawn prompt as skill](module-4-agent-teams/demo-16-spawn-prompt-as-skill/) | 4.7 | 6 | `/release-check <version>` with gates and stop conditions |
| 17 | [Competing hypotheses](module-4-agent-teams/demo-17-competing-hypotheses/) | 4.3 | 6 | a reproducer-driven debate that overturns the obvious answer |

## Conventions used in every demo

- **Scenario:** *Tidewater Books*, a fictional online bookstore (the labs use *Meridian*,
  so practising here is new material, not a replay).
- **README sections:** Why this demo · Files · Run it (copy-paste prompts) · What to
  observe / answer key · Discussion · Practice (after class).
- **Agents** use allowlists, `maxTurns`, and lowercase model aliases, and pass
  `python3 tools/lint_agents.py`.
- **Hooks** use `${CLAUDE_PROJECT_DIR}` paths, log or fail safely, and have tests.
- **Reset:** demos that change state ship `./reset.sh`.

## Safety

- Several demos mention `--dangerously-skip-permissions` – use it only in a disposable VM
  or container. Hooks still run under it (verified), but nothing else protects you.
- Demo 04 installs an agent into `~/.claude/agents/`. Run `./scope-demo.sh remove-user` afterwards.
- Everything here is fictional sample data. No real credentials are included.

## Versions

Claude Code changes quickly and agent teams are experimental. Where the course text and
current behaviour differ, the demos follow current documentation and
[`docs/version-notes.md`](docs/version-notes.md) lists every difference we know of,
including what we verified by running the demos.
