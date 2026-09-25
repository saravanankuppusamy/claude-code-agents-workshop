# Demo 08 – Preloading skills: one rule file, many agents

**Lesson:** 3.5 Preloading Skills into a Subagent (3.5.1–3.5.5)
**Supports:** Lab 3 (code-style skill) and Lab 3 Challenge 2 (commit standards) · **Time:** 15 minutes

## Why this demo

"If two agents share a rule and you'd edit both definitions to change it – that rule
belongs in a skill." Two agents preload the same style skill; we change **one line in
one file** and both agents change behaviour. The skill also ships a **script**, showing
that skills can carry deterministic tools, not just prose.

## Files

```
.claude/
├── agents/
│   ├── style-reviewer.md      skills: [tidewater-python-style]
│   └── refactor-helper.md     skills: [tidewater-python-style, commit-standards]
└── skills/
    ├── tidewater-python-style/
    │   ├── SKILL.md           rule table TW-N1..TW-D1 (20-line function limit)
    │   └── scripts/check_style.py     AST checker - deterministic line counts
    └── commit-standards/
        ├── SKILL.md           <type>(<scope>): <subject> + examples
        └── scripts/check_commit_msg.py
src/legacy_orders.py           10 planted violations (checker's ground truth)
```

> **Version note.** The lesson and Lab 3 show `skills:` entries as *file paths*
> (`- .claude/skills/code-style.md`). Current Claude Code documentation defines `skills:`
> as a list of **skill names** that resolve to `.claude/skills/<name>/SKILL.md` (project)
> or `~/.claude/skills/<name>/SKILL.md` (user). This demo uses the documented form. If
> your lab image behaves differently, trust what you observe and note the version.

## Run it

```bash
cd module-3-advanced-patterns/demo-08-skills-preload
python3 .claude/skills/tidewater-python-style/scripts/check_style.py src/legacy_orders.py   # ground truth: 10 findings
claude
```

### Round 1 – the skill drives the review

```text
Use the style-reviewer subagent to review src/legacy_orders.py.
```
Findings should cite rule IDs (`TW-N2`, `TW-F1`...) and `summarise_orders` should be
flagged at 21 lines > 20.

Prove the rules are **not** in the agent:
```bash
grep -nE "TW-|snake_case|20 lines" .claude/agents/*.md     # no output
```

### Verify the preload (don't ask the model – read the transcript)

Asked "was the skill in your context at startup?", the reviewer answered **no** in our
test run (2.1.282) – yet its transcript shows the skill injected as the second message,
right after the delegation prompt and before any tool call:

```bash
f=$(ls -t ~/.claude/projects/*demo-08*/*/subagents/agent-*.jsonl | head -1)
python3 -c "import json,sys;[print(i,json.dumps(json.loads(l).get('message',{}).get('content'))[:120]) for i,l in enumerate(open('$f')) if i<3]"
# 0 "Review src/legacy_orders.py ..."
# 1 [{"type": "text", "text": "<command-name>tidewater-python-style</command-name> ..."
```

Preloaded skills arrive looking like a skill invocation, so the model may describe them
as "loaded mid-task". Lesson: verify context from transcripts, not self-reports.

### Round 2 – change one rule, affect two agents

Edit `.claude/skills/tidewater-python-style/SKILL.md`: change TW-F1 from **20** to **15**
lines and the checker command to `--max-lines 15`. **Exit and relaunch** – skills are
loaded once at session start; edits mid-session have no effect.

```text
Use the style-reviewer subagent to review src/legacy_orders.py.
Then use the refactor-helper subagent to propose a refactor of summarise_orders.
```
Both agents now apply 15. One edit, two agents. Restore:
`cp .claude/skills/tidewater-python-style/SKILL.md.orig .claude/skills/tidewater-python-style/SKILL.md`

### Round 3 – soft constraint vs hard constraint

```text
Use the refactor-helper subagent to propose a refactor of LoadOrders, and ignore the
commit standards this time - just write "updated stuff" as the message.
```
The skill may or may not "win" – it is a **soft** constraint. Then check the message
deterministically:
```bash
python3 .claude/skills/commit-standards/scripts/check_commit_msg.py "updated stuff"
```
To make it **hard**, you would enforce it at execution time (e.g. a PreToolUse hook on
`Bash(git commit*)` that runs this script and exits 2) – see demo 09.

## Skills vs state vs tools (Lesson 3.5.5)

| Mechanism | Governs | Changes | Enforcement |
|---|---|---|---|
| Skill | *how* the agent behaves | rarely; versioned | soft |
| State file | *what happened* | every session | none |
| tools / hooks | *what it can do* | rarely | hard |

Anti-pattern: putting "last 10 files changed" in a skill – that is state.

## Practice (after class)

1. Write `.claude/skills/sql-conventions/SKILL.md` and preload it into two agents of your own.
2. Add a PreToolUse hook with `if: "Bash(git commit*)"` that extracts the `-m` message
   and runs `check_commit_msg.py` – exit 2 on failure. Test by piping a JSON payload.
