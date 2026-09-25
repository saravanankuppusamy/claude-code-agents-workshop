# Demo 02 – Built-in subagents vs. a custom subagent

**Lesson:** 2.3 Built-In Subagents, 2.3.2 Choosing Built-In vs. Custom
**Time:** 10 minutes

## Why this demo

The built-ins (**Explore**, **Plan**, **general-purpose**) are great for ad-hoc work.
A custom agent earns its place when you need *repeatable* output, a *narrower* tool
set, or a *specific model*. We run the same question through both and compare.

## Files

| File | Purpose |
|---|---|
| `tidewater/` | Six-module toy package with a real import graph |
| `.claude/agents/dependency-mapper.md` | Custom Haiku agent with a fixed output contract |

## Run it

```bash
cd module-2-subagents/demo-02-builtin-vs-custom
claude
```

### Round 1 – Built-in Explore

```text
Use the Explore agent to figure out which modules in tidewater/ depend on which.
```

### Round 2 – Built-in Plan

```text
Use the Plan agent to plan adding a "gift wrap" fee to orders. Do not change any files.
```

Point out: Plan decomposes and identifies affected modules (cart, pricing, orders) –
it is for *thinking before doing*.

### Round 3 – Custom agent

```text
Use the dependency-mapper subagent on tidewater/.
```

Run Round 3 **twice**. Then run Round 1 twice.

## What to compare

| Question | Explore (built-in) | dependency-mapper (custom) |
|---|---|---|
| Is the output format the same on both runs? | Usually varies | Fixed – mermaid + table |
| Which model ran? | Inherits parent (capped at Opus) | Haiku (cheap, fast) |
| Can it write files? | No – Explore is read-only | No – `tools: Read, Grep, Glob` |
| Could a teammate reuse it tomorrow? | Only by re-typing the prompt | Yes – it is a committed file |

**Expected mapping** (use it to judge accuracy): `storage` has the highest fan-in
(catalog, orders), `orders` has the highest fan-out (cart, storage, notify).

## Rules of thumb to leave on the whiteboard

- Ad hoc, once, default tools OK → **built-in**
- Repeated, shared, needs narrower tools or a specific model → **custom file**
- Prototype with a built-in, then *promote* the prompt that worked into a custom agent.

## Practice (after class)

1. Ask Claude: *"Turn the prompt I used in Round 1 into a custom agent file."* Diff
   the generated file against `dependency-mapper.md`. What did the generator leave out?
   (Hint: `maxTurns`, a tight `tools` list, and an output contract are commonly missing –
   see Lab 1 key takeaways.)
2. Add `effort: low` to `dependency-mapper.md`. Does quality change for this task?
