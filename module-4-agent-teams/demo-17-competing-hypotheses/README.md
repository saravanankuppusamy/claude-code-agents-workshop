# Demo 17 – Competing hypotheses: a debate that defeats anchoring

**Lesson:** 4.3 Common Team Patterns (hypothesis competition), 4.7 Coordination
**Supports:** Lab 6 (debugging with competing hypotheses) · **Time:** 30 minutes

## Why this demo

Lab 6's lead is told that the hypothesis explaining intermittency "is most likely the
root cause for an intermittent, concurrency-related fault" – which nudges it toward the
race condition. Real incidents punish that shortcut. In this bug:

* the **race condition is real** – but it causes *lost updates* (stock too **high**), not
  negative stock;
* the **stale cache** is what drives stock **negative** – and it reproduces with **no
  concurrency at all**;
* the **timezone** theory is quickly falsified.

"Only during rushes" is explained by a 5-second cache TTL (many orders inside one TTL
window), not by threads. Teammates who run reproducers and try to *disprove each other*
find this; a single agent that anchors on "intermittent ⇒ race" does not.

## Files

| File | Purpose |
|---|---|
| `BUG.md` | symptoms and the three hypotheses from stand-up |
| `shop/` | store (non-atomic decrement), cache (5 s TTL, never invalidated on sale), checkout (check → pay → act), restock |
| `repro/concurrent_orders.py` | `--serial`, `--no-cache`, `--trials`, `--buyers`, `--stock` – the experiment bench |
| `repro/restock_timezone.py` | probes H3 around midnight |
| `.claude/agents/hypothesis-investigator.md` | one teammate type: prediction first, reproducers only, challenge others |
| `.claude/agents/rca-lead.md` | Opus + `effort: high`, evidence-weighted rubric, anti-anchoring rule |
| `.claude/settings.json` | Bash allowed only for `python3 repro/*`; edits to `shop/` and `repro/` denied |
| `findings/TEMPLATE.md` | prediction · experiments · challenges · verdict |

## The experiment table (instructor answer key)

```bash
python3 repro/concurrent_orders.py                     # concurrent, cache on
python3 repro/concurrent_orders.py --no-cache          # concurrent, cache off
python3 repro/concurrent_orders.py --serial            # ONE buyer at a time, cache on
python3 repro/concurrent_orders.py --serial --no-cache # control
python3 repro/restock_timezone.py
```

| Condition | Negative stock | Lost updates | Reading |
|---|---|---|---|
| concurrent, cache on | 0/10 | 10/10 | race hides the symptom by writing a stale *higher* value |
| concurrent, cache off | 0/10 | 10/10 | race is real → oversell with positive stock |
| **serial, cache on** | **10/10** | 0/10 | **negative stock with zero concurrency → H2** |
| serial, cache off | 0/10 | 0/10 | control: correct |
| restock around midnight | never decreases | – | H3 refuted (only the report filename date shifts) |

Root cause of BUG-212: availability is checked against a cached value that sales never
invalidate, and the decrement has no floor. Fixes: atomic conditional decrement
(`UPDATE … SET stock = stock - ? WHERE stock >= ?`), invalidate/bypass the cache at
checkout. The lost-update race is a second bug the team should report.

## Run it

```bash
cd module-4-agent-teams/demo-17-competing-hypotheses
./reset.sh
claude
```
```text
Read BUG.md. Create an agent team to find the root cause. Spawn three teammates using the
hypothesis-investigator agent type, named h1, h2 and h3, owning H1 (race), H2 (stale cache)
and H3 (restock timezone) respectively. Tell each its hypothesis in its spawn prompt.
Have them talk to each other and try to disprove each other's theories, like a scientific
debate - each must send at least one challenge and answer the challenges it receives.
Gate: when all three findings/h1.md, h2.md, h3.md exist and each has a Verdict section,
spawn a teammate using the rca-lead agent type to write rca-report.md.
Stop condition: if any investigator cannot run the reproducers, stop and tell me.
```

### What to watch

- h1 runs the default experiment, sees **0 negative / 10 lost updates**, and has to
  concede its hypothesis doesn't produce the *specific* symptom. Good investigators
  report "CONTRIBUTING – real bug, different symptom".
- h2's `--serial` run is the decisive experiment. Watch whether h1 challenges it
  ("rushes only!") and how h2 answers (TTL window).
- h3 refutes itself within a few turns – that's success, not failure.
- Open `rca-report.md`: score table first, then cause, then "other bugs found".

## Discussion

1. Would a single agent investigating H1 → H2 → H3 serially have found this? Where
   would anchoring have kicked in?
2. Two teammates agree and one disagrees. When is agreement evidence, and when is it
   shared exposure to the same misleading signal? (Lab 6 Challenge 1 reflection.)
3. Why are the investigators allowed to *run* code but not *edit* it? Which layer
   enforces that (`.claude/settings.json` deny rules + allowlisted Bash prefix)?

## Practice (after class)

1. Fix the bug in a branch: atomic conditional decrement + cache bypass at checkout.
   Make all four experiment rows read 0/10 and 0/10.
2. Add an escalation protocol (Lab 6 Challenge 2): after three inconclusive
   experiments, an investigator writes `findings/<name>-escalation.md` and the lead
   redirects it to help the strongest hypothesis.
