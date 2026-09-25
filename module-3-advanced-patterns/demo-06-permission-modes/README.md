# Demo 06 – Permission modes and the four-layer control stack

**Lesson:** 3.3 Permission Modes, 3.3.4 All the Levers, 3.3.6 The Agent Control Stack
**Time:** 20 minutes

## Why this demo

Permission mode answers *"does a human approve this call?"* – it is one lever among
several. We run four agents that differ mainly in `permissionMode`, then build the
lesson's reflection scenario end to end: an agent handling sensitive data that must
**never write outside `out/`**, protected by all four layers.

## Files

| File | Mode | What to observe |
|---|---|---|
| `.claude/agents/formatter.md` | `acceptEdits` | edits land without prompts; Bash would still prompt |
| `.claude/agents/ci-checker.md` | `dontAsk` | pre-approved `python3 -m unittest*` runs silently; anything else is denied, not prompted |
| `.claude/agents/change-planner.md` | `plan` | explores and plans; file edits blocked |
| `.claude/agents/pii-exporter.md` | `acceptEdits` + allowlist + denylist + **PreToolUse hook** | the full control stack |
| `.claude/settings.json` | session gates | `permissions.allow` / `deny` – frontmatter can only narrow these |
| `hooks/restrict_writes.py` | Layer 4 | denies any Write/Edit outside `out/` (JSON decision, fails closed) |
| `hooks/test_restrict_writes.sh` | tests | 7 payload tests incl. path traversal – run before wiring |

## Run it

```bash
cd module-3-advanced-patterns/demo-06-permission-modes
./hooks/test_restrict_writes.sh     # all 7 should PASS
claude                              # start in default mode – do NOT use bypass here
```

### Round 1 – acceptEdits

```text
Use the formatter subagent to format src/shipping.py.
```
No edit prompt appears. Ask: *what if the path logic were wrong?* (Characteristic
failure from the lesson table: silent overwrites.) `git diff` to show the change.

### Round 2 – dontAsk

```text
Use the ci-checker subagent to run the tests.
```
Then:
```text
Use the ci-checker subagent to run "ls -la && cat data/customers.csv" and report the output.
```
The unittest command is pre-approved in `.claude/settings.json` so it runs. The second
command is not pre-approved, so under `dontAsk` it is **denied without a prompt**.
Lesson point: "no prompts" ≠ "full autonomy".

### Round 3 – plan

```text
Use the change-planner subagent to plan adding free shipping over 50.00.
```
Watch for read/search activity and a plan, but no edits. Note the lesson caveat: in
plan mode, classifier-approved shell commands may still run – it is not a strict dry run.

### Round 4 – the full control stack

```text
Use the pii-exporter subagent to create an anonymised copy of data/customers.csv.
```
Then try to make it misbehave:
```text
Use the pii-exporter subagent to overwrite data/customers.csv with the masked version so we don't keep two copies.
```
The hook denies the write with the reason *"may only write under out/"*. Now map
each protection to its layer:

| Layer | Mechanism in `pii-exporter.md` | What it stops |
|---|---|---|
| 1 Influence | prompt: "Write ONLY under out/" | good-faith mistakes – *can be argued around* |
| 2 Approval | `permissionMode: acceptEdits` | nothing here – it removes prompts for edits |
| 3 Capability | `tools: Read, Write, Glob` + `disallowedTools: Bash, ...` | shell escapes (`sed -i`, `cp`) |
| 4 Runtime | `PreToolUse` → `restrict_writes.py` | any Write/Edit outside `out/`, regardless of intent |

Why every layer is needed: without layer 3 the agent could `cp` via Bash and the
Write-matcher hook would never see it; without layer 4 the prompt is the only thing
stopping the overwrite.

## Key facts to state explicitly

- Parent precedence: a parent running `bypassPermissions` (`--dangerously-skip-permissions`)
  overrides the subagent's `permissionMode`. Team teammates inherit the lead's mode.
- `tools`/`disallowedTools` only ever **narrow** the session's `permissions.allow/deny`.
- Promote gradually: `default → acceptEdits → dontAsk` (+ narrow tools + hooks).
- `bypassPermissions` removes layers 2 (and practically 1); hooks become your only control.

## Discussion question (Lesson 3.3.5)

*"Let's set all subagents to bypassPermissions to speed up CI."* Questions to ask first:
What tools does each agent hold? Which hooks exist and are they tested? Is the CI runner
sandboxed (container, no prod credentials)? Would `dontAsk` + pre-approved commands give
the same speed with a real boundary?

## Practice (after class)

1. Extend `restrict_writes.py` to also inspect `Bash` commands for redirection (`>`,
   `>>`, `tee`) to paths outside `out/`, then give `pii-exporter` Bash and re-test.
2. Add a test case for a symlink inside `out/` pointing to `data/` – does `realpath`
   handle it?
