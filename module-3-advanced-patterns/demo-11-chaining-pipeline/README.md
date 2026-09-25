# Demo 11 – Chaining: a three-stage pipeline with transformation contracts

**Lesson:** 3.9.1 Chaining, 3.9.2 Orchestrator Pattern, 3.9.3 Design Rules
**Time:** 20 minutes

## Why this demo

"An unspecified format silently breaks when the model produces a reasonable variation."
Each stage here has a **written contract** (a JSON Schema), a **validator** at the
boundary, its **own model and tools**, and writes its output **to disk** so a failed
stage can be retried without re-running the ones before it.

```
input/support-tickets.txt
   │  ticket-extractor (haiku)  ── contracts/stage1-issues.schema.json
   ▼
pipeline/stage1-issues.json
   │  issue-triager (sonnet)    ── contracts/stage2-triage.schema.json
   ▼
pipeline/stage2-triage.json
   │  report-writer (haiku)
   ▼
pipeline/stage3-report.md
```

Why this model split: extraction and formatting are shallow and high-volume (Haiku);
clustering tickets by *root cause* needs judgment (Sonnet).

## Files

| File | Purpose |
|---|---|
| `.claude/agents/ticket-extractor.md` · `issue-triager.md` · `report-writer.md` | one agent per stage |
| `contracts/*.schema.json` | the stage boundary contracts |
| `tools/validate_contract.py` | stdlib-only schema validator (type/required/enum/pattern/minItems/maxLength) |
| `run-pipeline.sh` | headless `claude -p` version with validation gates and per-stage retry |
| `input/support-tickets.txt` | 20 messy tickets |

## Run it – inside a session (the orchestrator pattern)

```bash
cd module-3-advanced-patterns/demo-11-chaining-pipeline
claude
```
```text
Run the ticket pipeline as a chain of subagents, one at a time:
1. ticket-extractor on input/support-tickets.txt
2. After it finishes, run: python3 tools/validate_contract.py pipeline/stage1-issues.json contracts/stage1-issues.schema.json
   If INVALID, re-run ticket-extractor once with the validator output in its prompt, then stop if still invalid.
3. issue-triager, then validate pipeline/stage2-triage.json against contracts/stage2-triage.schema.json the same way.
4. report-writer.
Show me the final report and nothing else.
```
Note the **gates** ("if INVALID … stop") – the same idea as spawn-prompt gates in Module 4.

## Run it – headless (CI / cron)

```bash
./run-pipeline.sh              # stage 1 skipped if its output already exists
FORCE=1 ./run-pipeline.sh      # redo everything
```

## Break a contract on purpose

1. Edit `ticket-extractor.md`: delete the sentence "using only the enum values in the
   contract". Re-run stage 1 (`FORCE=1`). Likely result: `"category": "Payment issue"` –
   a *reasonable variation* – and the validator stops the pipeline at the boundary
   instead of letting stage 2 mis-cluster silently.
2. Hand-edit `pipeline/stage1-issues.json` to drop one ticket. Stage 2's rule "every
   ticket_id must appear exactly once" can't catch it – what check would? (Answer: a
   count check between stages – add it to `run-pipeline.sh`.)

## Answer key for the triage stage (use to judge output)

| Expected cluster | Tickets | Owner | Severity |
|---|---|---|---|
| Payment timeout → failed-but-charged / double charge | #101 #104 #107 #113 #119 | payments-team | critical |
| Receipt sent to wrong customer (PII leak) | #112 #116 | security-team | critical |
| ISBN search normalisation (hyphens, ISBN-10) | #102 #106 #117 | search-team | high |
| Member discount not applied | #109 #114 | payments-team or product | medium |
| Damaged / incomplete items | #103 #110 #118 | warehouse | medium |
| Unclustered / judgment calls | #105 (maybe joins payments – evenings), #108, #111, #115, #120 | – | – |

Good discussion: #105 ("slow in the evenings") and #119 ("Sunday night") hint that the
payment timeouts are load-related – exactly the kind of cross-ticket inference that
justified Sonnet for stage 2.

## Chain vs parallel (Lesson 3.9.6)

This work is **inherently sequential** – stage 2 cannot start without stage 1. If the
pipeline had branches that could run at the same time, it would have outgrown chaining
(see demo 12).

## Practice (after class)

- Add a stage 2b `owner-notifier` that runs **in parallel** with `report-writer` (both
  read stage 2) and writes one Markdown message per owner. Is it still a chain?
- Pin the stage models to full model IDs and explain when you would do that.
