# Demo 05 – Picking the right model for the job

**Lesson:** 2.8 Picking the Right Model, 2.8.2 Effort Levels, 2.8.4 Decision Framework
**Time:** 15 minutes (run the three triage agents in parallel to save time)

## Why this demo

"Match the model to the task, not the orchestrator." We run the **same** log-triage
task on Haiku, Sonnet and Opus against logs with a known **answer key**, then compare
accuracy, wall-clock time and tokens. Then we look at a task where the expensive model
*is* justified – a production migration review.

## Files

| File | Purpose |
|---|---|
| `generate_logs.py` | Creates deterministic noisy logs with three planted error patterns; prints the answer key |
| `.claude/agents/log-triage-{haiku,sonnet,opus}.md` | Identical prompts, different `model:` |
| `.claude/agents/migration-reviewer.md` | Opus + `effort: high` for a high-stakes review |
| `sample_migration.sql` | A migration with several real hazards |
| `worksheet.md` | Decision table students fill in (answers the lesson's Check Your Understanding) |

## Run it

```bash
cd module-2-subagents/demo-05-model-selection
python3 generate_logs.py          # note the ANSWER KEY it prints
claude
```

### Round 1 – same task, three models, in parallel

```text
Run the log-triage-haiku, log-triage-sonnet and log-triage-opus subagents in parallel
on the logs/ directory. When all three finish, show their tables side by side and
report each one's duration and token usage from the subagent results.
```

Compare with the answer key:

| Look for | Typical outcome |
|---|---|
| All three planted patterns found? | Usually yes for all three – the task is shallow |
| Counts correct? | Grep-based counting is deterministic; errors come from reading instead of grepping |
| Time / tokens | Haiku fastest and cheapest by a wide margin |

**Conclusion to draw:** for structured, high-volume scanning, Haiku gives the same
answer for a fraction of the cost. Opus buys nothing here.

### Round 2 – where depth pays

```text
Use the migration-reviewer subagent to review sample_migration.sql.
```

Hazards it should catch: `DROP COLUMN` data loss; `ADD COLUMN ... NOT NULL` with no
default on a populated table; the `UPDATE` leaves unshipped rows without a valid status;
index creation lock; unrelated, irreversible `DELETE FROM customers`.
Optionally rerun it as a Haiku agent and compare what it misses.

### Round 3 – effort is a separate dial

Edit `log-triage-sonnet.md`, add `effort: low`, rerun. Output length and time drop;
accuracy on this task should not. Effort does not appear in the lesson's frontmatter
table but current Claude Code accepts it per agent (`low | medium | high | xhigh | max`).

## Talking points

- Subagent model is independent of the orchestrator: a Sonnet lead can fan out Haiku workers.
- Use aliases (`haiku`, `sonnet`, `opus`, `fable`) day to day; pin full IDs in production
  pipelines so behaviour does not change underneath you.
- Model resolution order (current docs): per-call `model` › agent `model:` ›
  `CLAUDE_CODE_SUBAGENT_MODEL` › parent's model.

## Practice (after class)

Complete `worksheet.md` for three agents from your own work. Then run
`python3 generate_logs.py 200 1000` and repeat Round 1 – where does each model start to
struggle, and does raising `maxTurns` or switching to Grep-only instructions fix it?
