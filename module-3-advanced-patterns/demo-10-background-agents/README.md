# Demo 10 – Background subagents: manifest, heartbeat, idempotency

**Lesson:** 3.8 Foreground vs. Background Execution (3.8.1–3.8.5)
**Time:** 15 minutes

## Why this demo

A background agent that fails silently leaves no trace. The lesson lists five
reliability patterns – **well-known output path, structured manifest, heartbeat,
incremental output, explicit error capture** – plus **idempotency**. This demo has an
indexer that implements all of them and two small tools that let the orchestrator (or
you, or CI) monitor and *verify* the result before consuming it.

## Files

| File | Purpose |
|---|---|
| `.claude/agents/review-indexer.md` | `background: true`, `permissionMode: acceptEdits`, no Bash, strict file ownership |
| `make_corpus.py` | generates 120 review files in `corpus/` |
| `tools/watch_manifest.py` | polls manifest + heartbeat; exit codes done/failed/stalled/not-started |
| `tools/validate_index.py` | checks completeness, duplicates and record-vs-source agreement |
| `reset.sh` | clears outputs and regenerates the corpus |

## Run it

```bash
cd module-3-advanced-patterns/demo-10-background-agents
./reset.sh
claude
```
```text
Use the review-indexer subagent to index the reviews.
```
The orchestrator returns immediately – the indexer runs in the background. Keep talking
to the main session:
```text
While that runs, explain what the "sentiment" rule in the indexer is.
```
In a **second terminal**:
```bash
python3 tools/watch_manifest.py          # running 20/120 ... running 40/120 ... DONE
tail -f index/progress.log
```
In Claude Code, `/tasks` lists running and finished background agents.

When done:
```bash
python3 tools/validate_index.py          # INDEX OK - or a precise list of problems
```

### Idempotency

```text
Use the review-indexer subagent to index the reviews.
```
Second run: *"Index already current"*. Then `python3 make_corpus.py 130` and run again –
the file count changed, so it re-indexes from scratch (overwrite, never duplicate).

### Failure capture

`chmod -w index` then re-run. The agent should record `"status": "failed"` with an error
rather than vanishing. `watch_manifest.py` exits 1. `chmod +w index` to restore.

## Three ways to control foreground/background

| Where | How | Scope |
|---|---|---|
| Agent frontmatter | `background: true` | every invocation |
| Agent tool call | `run_in_background: true/false` | one invocation |
| At runtime | `Ctrl+B` on a running foreground subagent | detach now |

## Design rules to state

- Background agents **cannot ask you anything** – pre-configure permissions
  (here: `acceptEdits` + no Bash) or prompts will fail.
- The orchestrator should consume output only after `status: done` **and** validation.
- Separate the **progress log** (for humans) from the **result** (for machines).
- `validate_index.py` compares records to their source files – the only defence against
  a background agent that "summarises" work it didn't do.

## Practice (after class)

1. Kill the session mid-run. Is the partial `reviews.jsonl` usable? Change the protocol
   so a re-run *resumes* from `files_done` instead of starting over.
2. Add a `SubagentStop` hook in `.claude/settings.json` that runs `validate_index.py` and
   writes the result into the manifest as `"validated": true/false`.
