# Module 3 – Advanced Subagent Patterns

Companion demos for **Lesson 3** of WA3877 and **Labs 3–4**.

| Demo | Lesson section | Pairs with | What students see |
|---|---|---|---|
| [06 – Permission modes & control stack](demo-06-permission-modes/) | 3.3 | – | `acceptEdits`, `dontAsk`, `plan`; a PII agent protected by all four layers |
| [07 – Memory & state](demo-07-memory-and-state/) | 3.4, 3.6.2 | Lab 3 | `memory: project` vs file-backed state; schema, validator, pruning, SubagentStop gate |
| [08 – Skills preload](demo-08-skills-preload/) | 3.5 | Lab 3 | one skill, two agents; skills that ship scripts |
| [09 – Hooks: guard & audit](demo-09-hooks-guard-and-audit/) | 3.6–3.7 | Lab 4 | naive vs robust guard, `updatedInput`, JSONL audit, rate limit, `if:` |
| [10 – Background agents](demo-10-background-agents/) | 3.8 | – | manifest + heartbeat + idempotency + output validation |
| [11 – Chaining pipeline](demo-11-chaining-pipeline/) | 3.9.1–3.9.3 | – | three-stage chain with JSON contracts, in-session and `claude -p` |
| [12 – Parallel research & noisy ops](demo-12-parallel-and-noisy/) | 3.9.4–3.9.6, 3.10 | Lab 5 warm-up | fan-out researchers + a test runner that keeps 2,000 lines out of your context |

## The agent control stack (Lesson 3.3.6)

| Layer | Mechanism | Nature | Demo |
|---|---|---|---|
| 1 Influence | system prompt, skills, CLAUDE.md | soft – can be reasoned around | 08 |
| 2 Approval | `permissionMode` | who approves each call | 06 |
| 3 Capability | `tools` / `disallowedTools` / `permissions` | hard – what exists | 03, 06 |
| 4 Runtime | hooks | hard – inspects every call | 06, 07, 09 |

*State records what happened; skills define how the agent behaves; tools and hooks
enforce what it can do.*
