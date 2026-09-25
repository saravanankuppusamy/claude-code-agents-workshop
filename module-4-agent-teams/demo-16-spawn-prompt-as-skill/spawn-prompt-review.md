# Spawn prompt review: bad vs good

The spawn prompt is the orchestrator's only briefing (Lesson 4.7.1). Three things
belong in every one: **which agents**, **sequencing & gates**, **stop conditions**.

## Bad

```text
Get a team together to check if the release is ready and write up the results.
```

| Missing | What the orchestrator will improvise |
|---|---|
| Which agents | invents generic teammates with default tools and models |
| Output paths | teammates choose filenames → lead can't find them, or they collide |
| Gate | lead starts synthesising after the first teammate finishes |
| Stop condition | proceeds even if the changelog has no entry for the version |
| Decision format | prose instead of a GO/NO-GO the pipeline can act on |

## Better – but still leaky

```text
Spawn test-gap-finder, changelog-verifier and config-auditor, then have the lead write
a release report when they're done.
```

"When they're done" is **not** a gate – it's a hope. Lab 6's failure (debug-lead spawned
before both reviewers finished) is exactly this. A gate names a *checkable condition*:
"all three findings files exist and are non-empty".

## Good

See `.claude/skills/release-check/SKILL.md`. Every decision is explicit: names, agent
types, artifact per teammate, the checkable gate, three stop conditions, and a
machine-readable first line.

## Exercise

Rewrite this Lab 6 prompt fragment as an explicit gate + stop condition:

> "When both teammates have completed their investigations and gone idle, spawn debug-lead."

One answer: *"Before spawning debug-lead, confirm with Glob that findings/hypothesis-a.md
and findings/hypothesis-b.md both exist, and read tasks.md to confirm T-001 and T-002 are
done. If either check fails, do not spawn debug-lead; report which check failed and stop."*
