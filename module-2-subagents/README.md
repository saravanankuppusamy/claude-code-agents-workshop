# Module 2 – Creating and Configuring Subagents

Companion demos for **Lesson 2** of WA3877 and **Labs 1–2**.

| Demo | Lesson section | Pairs with | What students see |
|---|---|---|---|
| [01 – Context isolation](demo-01-context-isolation/) | 2.2 | before Lab 1 | A probe agent proves the `prompt` is the only task-specific channel |
| [02 – Built-in vs custom](demo-02-builtin-vs-custom/) | 2.3 | before Lab 1 | Explore/Plan vs a custom agent with a fixed output contract |
| [03 – Allowlist vs denylist](demo-03-allowlist-vs-denylist/) | 2.6–2.7 | Lab 1 | A "read-only" denylist agent edits a file via Bash; a linter catches silent failures |
| [04 – Scope precedence](demo-04-scope-precedence/) | 2.5 | Lab 2 | Session › project › user, plus `--agents` vs `--agent` |
| [05 – Model selection](demo-05-model-selection/) | 2.8 | Lab 2 | Same task on Haiku/Sonnet/Opus against an answer key |

## The three design decisions (put this on the board)

| Decision | Lever | Default stance |
|---|---|---|
| What does it do? | system prompt body + `description` | write `description` for the orchestrator, not for humans |
| What can it touch? | `tools` / `disallowedTools` | start from the minimal allowlist; add only on proven need |
| How capable must it be? | `model`, `effort`, `maxTurns` | cheapest model that passes your answer key; always set `maxTurns` |

## Minimal, safe agent template

```markdown
---
name: my-agent                 # lowercase-hyphens
description: <when the orchestrator should use this agent – be specific>
model: haiku                   # haiku | sonnet | opus | fable | inherit | full id
maxTurns: 8                    # circuit breaker
tools: Read, Grep, Glob        # allowlist – prefer this over disallowedTools
---

<system prompt: role, procedure, exact output format>
```

Lint it: `python3 tools/lint_agents.py .claude/agents`
