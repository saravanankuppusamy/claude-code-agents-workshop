# Demo 16 – Spawn prompts as versioned skills (and commands)

**Lesson:** 4.7.1 The Spawn Prompt, 4.7.2 Custom Commands: Storing the Spawn Prompt
**Supports:** Lab 6 Challenge 1 (`/run-investigation`) · **Time:** 15 minutes

## Why this demo

A spawn prompt that works is a design artefact, like an agent definition. Kept in
terminal history, it is "one session close away from being lost". Here the same team
workflow is stored twice – as a **skill** (current recommended format) and as a
**legacy command** – and the prompt itself is dissected against the three required
decisions: agents, gates, stop conditions.

## Files

| File | Purpose |
|---|---|
| `.claude/skills/release-check/SKILL.md` | `/release-check 2.4.0` – `$ARGUMENTS`, `disable-model-invocation: true` |
| `.claude/commands/release-check-legacy.md` | same workflow as a `.claude/commands/` file: `$1`, `` !`ls src` `` inline bash, `@CHANGELOG.md` include, `allowed-tools` |
| `.claude/agents/{test-gap-finder,changelog-verifier,config-auditor}.md` | the teammate types |
| `spawn-prompt-review.md` | bad → leaky → good, and a gate-rewriting exercise |
| `src/`, `tests/`, `CHANGELOG.md` | a release candidate with real problems |

## Run it

```bash
cd module-4-agent-teams/demo-16-spawn-prompt-as-skill
claude
```
```text
/release-check 2.4.0
```
Expected **NO-GO**: `DEBUG = True` and `PAYMENT_SANDBOX = True` are blockers;
`gift_wrap_total` and `bulk_discount` have no tests; "Removed legacy PayPal Classic
integration" has no evidence in `src/`.

Now test a stop condition:
```text
/release-check 9.9.9
```
The lead should stop without spawning anyone (no changelog section).

Compare the legacy form:
```text
/release-check-legacy 2.4.0
```
Point out what the command's pre-processing did *before* Claude saw the prompt: the
`` !`ls src` `` output and the contents of `CHANGELOG.md` are already inlined.

## Why `disable-model-invocation: true`?

Skills can be invoked by Claude autonomously when their description matches. A skill
that **spawns a team** costs several times a normal session's tokens – you want it to
run only when a human types `/release-check`. Note the consequence: skills with this
flag can't be preloaded into a subagent via `skills:`.

## Skills vs commands (Lesson 4.7.2 note)

| | `.claude/skills/<name>/SKILL.md` | `.claude/commands/<name>.md` |
|---|---|---|
| Invoke | `/name args` | `/name args` |
| Arguments | `$ARGUMENTS` (also `$0`, `$1`…) | `$ARGUMENTS`, `$1`, `$2`… |
| Claude may auto-invoke | yes, unless `disable-model-invocation: true` | no |
| Can bundle scripts/references | yes (folder) | no (single file) |
| Status | recommended | still works |

Name files after the **workflow** (`release-check`), not the roster
(`spawn-tests-changelog-config`) – workflows are stable, rosters change.

## Practice (after class)

1. Work through the exercise at the bottom of `spawn-prompt-review.md`.
2. Add a fourth teammate (`dependency-auditor` over a `requirements.txt`) by editing
   *only* the skill and adding one agent file. Commit both – the diff is your change record.
3. Convert Lab 6's Phase 2 prompt into `.claude/skills/run-investigation/SKILL.md`.
