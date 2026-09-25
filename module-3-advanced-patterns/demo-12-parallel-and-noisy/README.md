# Demo 12 – Parallel research and isolating noisy operations

**Lesson:** 3.9.4 Parallel Research, 3.9.5 Isolating Noisy Operations, 3.10 Subagent vs Main Conversation
**Bridges to:** Lab 5 (parallel code review) and Module 4 · **Time:** 20 minutes

## Why this demo

Two patterns, one incident:

1. **Fan-out / fan-in research.** Three independent researchers (auth, payments,
   search) investigate at the same time, each writing to *its own* findings file. The
   orchestrator synthesises. The twist: the three symptoms turn out to be **linked**
   (short, predictable session tokens), which only the synthesis step can see.
2. **Noisy operation isolation.** A 400-test suite prints ~2,000 lines. A Haiku
   `test-runner` absorbs the noise and returns three sentences.

## Files

| File | Purpose |
|---|---|
| `INCIDENT.md` | three symptoms, three suspected areas |
| `app/auth`, `app/payments`, `app/search` | small modules with planted, *interacting* bugs |
| `.claude/agents/area-researcher.md` | ONE generic definition, invoked 3× with different scopes; writes only to `findings/` (hook) |
| `.claude/agents/test-runner.md` | Haiku; full log to `reports/test-run.log`, 3-sentence reply |
| `hooks/restrict_writes.py` | same hook as demo 06 – reused, not rewritten |
| `tests/test_catalog_bulk.py` | 400 noisy tests, 2 planted failures (cases 137 and 311) |

## Part 1 – Fan-out / fan-in (12 min)

```bash
cd module-3-advanced-patterns/demo-12-parallel-and-noisy
claude
```
```text
Investigate INCIDENT.md with three area-researcher subagents running in parallel:
- app/auth     -> findings/auth.md
- app/payments -> findings/payments.md
- app/search   -> findings/search.md
Give each one the incident file, its area and its findings file in the prompt.
When all three are done, read the three findings files and write findings/synthesis.md:
are these one root cause or three? Rank the fixes.
```

Watch for: three agents active at once; each Reads only its own area; three separate
files (no write races). Then read `findings/synthesis.md`.

**Answer key**

| Symptom | Local cause | Area |
|---|---|---|
| 1 Logged out mid-checkout | TTL cut to 15 min, absolute (not sliding) expiry | auth |
| 2 Charged twice | new idempotency key on retry after timeout | payments |
| 3 Another customer's "recently viewed" | cache key = first 6 chars of token | search |
| **Cross-cutting** | tokens are `<user>-<epoch>`: predictable and collide; search's key truncation makes collisions common | auth ↔ search |

A good synthesis notices symptom 2 is independent while 1 and 3 share the token design.
That link is what the **"Links to other areas"** section in each findings file is for.

Discussion: would an **agent team** have done better here? Only if researchers needed
to talk *during* the run (e.g. search researcher asking auth "what is the token
format?"). With independent areas and one synthesis at the end, parallel subagents are
sufficient – Lesson 4.2.2.

## Part 2 – Keep the noise out of your context (8 min)

First, the wrong way – in the main conversation:
```text
Run python3 -m unittest discover -s tests -v and tell me what failed.
```
Run `/context` and note how much of the window the test output consumed.

Now start a fresh session (`/clear`) and do it the right way:
```text
Use the test-runner subagent.
```
Expected reply: *"400 run, 398 passed, 2 failed: test_case_137 and test_case_311 (VAT
mismatch)… Full log: reports/test-run.log"*. Run `/context` again – the difference is
the point. The subagent's context window was sacrificed, not yours.

## When NOT to use a subagent (Lesson 3.10.3)

Ask the class which of these deserve a subagent:
- "What does `SESSION_TTL_SECONDS` do?" → **no**, short, inline
- "Run the 400 tests" → **yes**, noisy
- "Let's debug the checkout together step by step" → **no**, interactive and needs full context
- "Scan every module for hard-coded secrets" → **yes**, parallelisable and noisy

## Practice (after class)

1. Convert Part 1 into three **distinct** agent definitions (one per hypothesis, as the
   lesson recommends). What do you gain (scoped tools, tailored prompts) and lose
   (duplication)? Could a shared skill remove the duplication?
2. Make the test-runner write `reports/test-summary.json` (`run`, `passed`, `failed`,
   `failures[]`) so a later chain stage can consume it without parsing prose.
