# Demo 03 – Allowlist vs. denylist: watch a "read-only" agent write a file

**Lesson:** 2.6.2 Tool Permissions, 2.7 Tool Allowlists and Denylists
**Supports:** Lab 1 (read-only code reviewer) · **Time:** 15 minutes

## Why this demo

The lesson's `MultiEdit ← FORGOTTEN` example is the classic denylist failure mode.
In current Claude Code the more dramatic leak is **Bash**: a reviewer that denies
`Write` and `Edit` can still change a file with `sed -i`. Seeing it happen is far more
persuasive than reading about it.

> Rule to internalise: **a missing allowlist entry fails loudly (the tool is simply
> unavailable); a missing denylist entry fails silently (the tool quietly works).**

## Files

| File | Purpose |
|---|---|
| `src/inventory.py` | Small file with a comment typo ("tpyo") and naming issues |
| `.claude/agents/reviewer-denylist.md` | `disallowedTools: Write, Edit` – forgot Bash, NotebookEdit |
| `.claude/agents/reviewer-allowlist.md` | `tools: Read, Grep, Glob` – nothing else exists for it |
| `broken-examples/` | Three agent files with silent-failure bugs for the linter demo |
| `reset.sh` | Restores `src/inventory.py` between runs |

## Run it

```bash
cd module-2-subagents/demo-03-allowlist-vs-denylist
claude
```

### Round 1 – both agents can review

```text
Use the reviewer-allowlist subagent to review src/inventory.py.
```

### Round 2 – ask each one to "fix the typo"

```text
Use the reviewer-denylist subagent to fix the typo "tpyo" in the comment in src/inventory.py.
```

**Expected:** Write and Edit are blocked, so the agent tries another route – typically
`Bash` with `sed -i 's/tpyo/typo/' src/inventory.py`. Depending on your permission mode
you may get a Bash permission prompt. **Approve it** so the class sees the file change:

```bash
git diff --no-index src/inventory.py.orig src/inventory.py
```

```text
Use the reviewer-allowlist subagent to fix the typo "tpyo" in the comment in src/inventory.py.
```

**Expected:** it cannot. It has no tool that writes, so it reports the fix instead.

Run `./reset.sh` afterwards.

### Round 3 – make silent failures loud with the linter

```bash
python3 ../../tools/lint_agents.py .claude/agents broken-examples
```

Walk through the output:

| File | What the linter catches | Why it matters |
|---|---|---|
| `reviewer-denylist.md` | denylist-only, Bash/NotebookEdit still reachable | the leak you just watched |
| `broken-examples/tabbed-reviewer.md` | TAB in frontmatter | YAML error → file silently ignored |
| `broken-examples/typo-tools.md` | `grep` wrong case, `GlobTool` unknown, no `maxTurns` | unknown names are dropped silently |
| `broken-examples/leaky-readonly.md` | says read-only but has `Bash` | Bash can write (`>`, `tee`, `sed -i`) |

## Discussion questions

1. When is a denylist the *right* choice? (Lesson table 2.7.2: "full-stack executor" –
   broad agent, block one or two dangerous tools.)
2. The reviewer's prompt says "you never modify files" and it still did. Which layer of
   the control stack (Lesson 3.3.6) actually protects you?
3. Your reviewer genuinely needs to run `pytest`. How do you give it Bash without giving
   it `sed -i`? (Preview of Module 3: `permissions.allow`/`deny` rules and PreToolUse hooks.)

## Practice (after class)

- Add `Bash` to `reviewer-allowlist` and repeat Round 2. Then write a PreToolUse hook
  that blocks Bash commands containing `-i`, `>`, `tee`, or `mv` (see demo 09 for a
  hook template).
- Run `python3 ../../tools/lint_agents.py --all` from anywhere in the repo to lint every
  agent in the workshop.
