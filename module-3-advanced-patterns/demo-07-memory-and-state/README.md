# Demo 07 – Persistent memory: platform `memory:` vs. file-backed state

**Lesson:** 3.4 Persistent Memory Across Sessions (3.4.1–3.4.7), 3.6.2 SubagentStop
**Supports:** Lab 3 (project-tracker) and its Challenge 1 (structured schema) · **Time:** 25 minutes

## Why this demo

Lab 3 builds file-backed state by hand. This demo puts it next to the **platform
`memory:` field**, adds the pieces Lab 3 leaves as reflection questions – a pinned
**schema**, a **validator**, a **pruning** strategy – and replaces "please remember to say
wrap up" with a **SubagentStop hook that refuses to let the agent stop without recording
state**.

## Files

| File | Purpose |
|---|---|
| `.claude/agents/style-coach.md` | Option A – `memory: project` (platform-managed directory) |
| `.claude/agents/session-tracker.md` | Option B – file-backed state + schema + Stop hook |
| `.claude/memory/state-template.md` | Pinned schema v2 (6 fields + end marker) |
| `.claude/memory/project-state.md` | Seed state with one prior session |
| `hooks/require_state_entry.py` | SubagentStop gate: exit 2 if wrap-up requested but state not written |
| `tools/validate_state.py` | Detects truncation, schema drift, bad dates, overgrowth |
| `tools/prune_state.py` | Archives old sessions, carries decisions/open questions forward, atomic write |
| `tests/fixtures/corrupted-state.md` | A truncated entry (interrupted write) |
| `tests/make_big_state.py` | Generates 60 sessions to demo overgrowth + pruning |

## Part A – Platform memory (5 min)

```bash
cd module-3-advanced-patterns/demo-07-memory-and-state
claude
```
```text
Use the style-coach subagent to review src/search.py.
```
```text
Tell the style-coach subagent: our team prefers early returns over nested ifs, and we
never flag one-letter loop variables. It should remember that.
```
Exit, then look on disk:
```bash
ls .claude/agent-memory/style-coach/ && cat .claude/agent-memory/style-coach/MEMORY.md
```
Relaunch and review `src/recommend.py` – the preferences are applied.

Points to make: platform memory lives at `.claude/agent-memory/<agent>/` (`project`),
`~/.claude/agent-memory/<agent>/` (`user`) or `.claude/agent-memory-local/<agent>/`
(`local`, not committed). The first ~200 lines of `MEMORY.md` are injected at startup
and Read/Write/Edit are auto-enabled for that directory. You don't choose the schema.

## Part B – File-backed state with a schema (10 min)

```text
Use the session-tracker subagent to start a session.
```
It should quote the 2026-09-18 decision and open question verbatim. Then:
```text
Use the session-tracker subagent to look at src/recommend.py and tell me whether ties
in also_bought are ordered deterministically.
```
```text
I've decided ties should be broken by ISBN ascending. Ask the session-tracker subagent to wrap up.
```
```bash
python3 tools/validate_state.py        # VALID (2 sessions)
cat .claude/memory/project-state.md
```

### Break it on purpose (Lab 3's "edit the state file" moment, extended)

```bash
cp tests/fixtures/corrupted-state.md .claude/memory/project-state.md
python3 tools/validate_state.py        # INVALID – truncated entry
```
Start a new session – the agent's startup protocol should *flag* the truncated entry
rather than silently trusting it. Restore with `./reset.sh` (also clears the style-coach memory).

## Part C – Make shutdown automatic with a SubagentStop hook (5 min)

`session-tracker.md` registers a `Stop` hook in its frontmatter (Claude Code converts a
subagent's `Stop` to `SubagentStop`). When the agent is asked to wrap up but the state
file hasn't been modified in the last 15 minutes, the hook exits **2** and its stderr –
*"Before you stop: append this session's entry…"* – goes back to the agent, which then
writes the entry. `stop_hook_active` prevents an infinite loop.

Test it without Claude:
```bash
export CLAUDE_PROJECT_DIR=$PWD
touch -d '1 hour ago' .claude/memory/project-state.md
echo "{\"cwd\":\"$PWD\"}" | python3 hooks/require_state_entry.py; echo "exit=$?"   # 2
echo '{"stop_hook_active":true}' | python3 hooks/require_state_entry.py; echo "exit=$?"   # 0
```

## Part D – Overgrowth and pruning (5 min)

```bash
python3 tests/make_big_state.py > /tmp/big-state.md
python3 tools/validate_state.py /tmp/big-state.md          # INVALID: 60 sessions
python3 tools/prune_state.py --keep 10 /tmp/big-state.md
python3 tools/validate_state.py /tmp/big-state.md          # VALID: 10 sessions
head -30 /tmp/big-state.md                                 # carried-forward block
```
This is one answer to Lesson 3 reflection Q5 (200 entries, inconsistent behaviour):
archive, carry forward the durable facts, and teach the startup protocol to read the
carried-forward block first.

## Choosing (Lesson 3.4.7)

| Need | Use |
|---|---|
| Simple "remember what you learned about this repo" | `memory: project` |
| Team-defined schema, specific path, reviewed in PRs, multi-agent readers | file-backed state |
| Stable rules (naming, formats) | a **skill** (demo 08), not state |
| Must block something | `tools` / hooks, not state or skills |

Neither option is transactional. For concurrent writers use one writer per file, or
append-only writes with a lock (see `hooks/rate_limit.py` in demo 09 for an `fcntl` lock).

## Practice (after class)

1. Add a `schema_version:` line to the template and teach `validate_state.py` to
   migrate v1 entries (Lab 3 Challenge 1 reflection: schema migration).
2. Add a `PreCompact` hook in `.claude/settings.json` that copies the state file to
   `.claude/memory/snapshots/` before compaction.
