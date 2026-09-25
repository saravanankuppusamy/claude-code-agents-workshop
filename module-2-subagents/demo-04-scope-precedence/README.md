# Demo 04 – Scope precedence: session › project › user › plugin

**Lesson:** 2.5 Scoping: Where a Subagent Lives
**Supports:** Lab 2 (project vs. user `sql-writer`) · **Time:** 15 minutes

## Why this demo

Three definitions share the name `release-notes`. Each one stamps its **scope and model
on the first line of its output**, so the class can see instantly which definition won.
Lab 2 shows project-vs-user; this demo adds the **session scope** (`--agents`) and the
**`--agent`** (singular) flag, which students routinely confuse.

## Files

| File | Scope | Model | Output style |
|---|---|---|---|
| `session-scope/agents.json` | Session (`--agents`) | haiku | one tweet-length line |
| `.claude/agents/release-notes.md` | Project | haiku | terse bullets |
| `user-scope/release-notes.md` → `~/.claude/agents/` | User | sonnet | warm, customer-facing |
| `scope-demo.sh` | helper: install/remove the user agent safely, launch session scope | | |
| `CHANGES.txt` | input for all three | | |

## Run it

```bash
cd module-2-subagents/demo-04-scope-precedence
./scope-demo.sh install-user        # put a same-named agent at user scope
./scope-demo.sh status
```

### Round 1 – Project beats User

```bash
claude
```
```text
Use the release-notes subagent to write release notes.
```
Expect `[release-notes | scope=PROJECT | model=haiku]`.

### Round 2 – Session beats Project

```bash
./scope-demo.sh session             # = claude --agents "$(cat session-scope/agents.json)"
```
```text
Use the release-notes subagent to write release notes.
```
Expect `scope=SESSION`. Exit and relaunch plain `claude` – the session agent is gone
(ephemeral).

### Round 3 – User wins when there is no project definition

```bash
cd ..            # leave the project directory (no .claude/agents/release-notes.md here)
claude
```
```text
Use the release-notes subagent to write release notes for demo-04-scope-precedence/CHANGES.txt
```
Expect `scope=USER | model=sonnet`.

### Round 4 – `--agent` (singular) is a different thing

```bash
cd demo-04-scope-precedence
claude --agent release-notes
```
```text
Write release notes.
```
There is no delegation: the **whole session** runs as `release-notes` (its prompt,
tools and model). Try asking it to edit a file – it only has `Read`.

### Clean up (important – user scope persists across all projects)

```bash
./scope-demo.sh remove-user
```

## Cheat sheet to leave on screen

| You type | What it does | Scope created |
|---|---|---|
| `claude --agents '{json}'` | Defines extra agents for this session | Session (highest) |
| `claude --agent name` | Runs the *main* session as that agent | none – it is not a subagent |
| `.claude/agents/x.md` | Project agent, commit it | Project |
| `~/.claude/agents/x.md` | Personal agent, all projects | User |
| plugin `agents/` | Distributed agent; no hooks/permissionMode/mcpServers | Plugin (lowest) |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | Enables teams – **neither flag above does** | – |

> Current docs also list **managed settings** (organisation policy) above session scope.

## Discussion questions

1. When is a same-name collision *intentional*? (A team "override" of a personal agent
   inside a regulated repo – exactly Lab 2's SELECT-only `sql-writer`.)
2. A developer says "my agent ignores my edits". What is the first thing you check?
   (A higher-precedence definition with the same name.)
3. Why might you prefer a *distinct* name (`release-notes-dev`) over a same-name override?

## Practice (after class)

Add a fourth definition in a **nested** folder: `sub/.claude/agents/release-notes.md`,
then launch `claude` from `sub/`. Current docs say the closest `.claude/agents/` wins
when walking up from the working directory. Verify it.
