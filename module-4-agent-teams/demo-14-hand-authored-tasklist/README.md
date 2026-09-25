# Demo 14 – Hand-authored task lists: dependencies, self-claiming, collisions

**Lesson:** 4.4.3–4.4.5 Task List Anatomy & Patterns, 4.6 Task Dependencies and Self-Claiming
**Supports:** Lab 6 (hand-authored `tasks.md`) · **Time:** 25 minutes

## Why this demo

The lesson says collisions are "rare but possible – the task list has no transactional
write mechanism", and teaches the lead to *detect* them. This demo first **shows the
race happening** (8 simulated teammates, 1 task, 8 claims), then removes it by giving
teammates a claim tool that locks. Detection still matters – `check` finds seven other
kinds of task-list rot – but prevention is better.

## Files

| File | Purpose |
|---|---|
| `tasks.md` | 7 tasks; T-006 requires five tasks; T-007 requires T-006 |
| `tools/tasklist.py` | `show`, `next`, `claim`, `claim-next`, `done`, `release`, `check`, `reset` – locked + atomic |
| `tools/race_demo.py` | `naive` vs `locked` claiming by 8 concurrent processes |
| `fixtures/tasks-broken.md` | every failure mode at once, for `check` |
| `.claude/agents/doc-writer.md` | teammate with the self-claiming protocol (uses the tool, never hand-edits) |
| `.claude/agents/docs-lead.md` | lead: collision check after each completion, stall handling |
| `src/*.py` | five undocumented modules to document |
| `tests/test_tasklist.py` | 7 tests incl. a 10-process concurrent claim |

## Part 1 – See the race (no Claude needed, 3 min)

```bash
cd module-4-agent-teams/demo-14-hand-authored-tasklist
python3 tools/race_demo.py naive
python3 tools/race_demo.py locked
```
Typical naive output: `T-001: writer-1, writer-0, writer-2 ... <-- DUPLICATE WORK` and
the file ends up showing only the **last** writer. That is the lesson's collision
scenario (4.6 Check Your Understanding) – and the file itself no longer shows the
evidence, which is why *detection after the fact* is weak.

## Part 2 – The lead's integrity check (3 min)

```bash
python3 tools/tasklist.py check --file fixtures/tasks-broken.md
```
| Finding | Lesson link |
|---|---|
| `COLLISION: T-003 appears 2 times` / `multiple owners` | 4.6.2 collision detection |
| `open but owned by` / `claimed but no owner` | half-finished claim or release |
| `ordering violated` | `requires:` bypassed |
| `WRITE RACE RISK: artifact shared` | 4.9.3 one artifact per task |
| `DEADLOCK: dependency cycle` | 4.9.5 coordination deadlock |
| `done but artifact does not exist` | teammate "finished" without output |

## Part 3 – Run the team (15 min)

```bash
./reset.sh
claude
```
```text
Create an agent team for the API documentation backfill in tasks.md. Spawn two teammates
using the doc-writer agent type, named doc-writer-1 and doc-writer-2. Each follows its
self-claiming protocol until no eligible work remains. You are the lead: follow the
docs-lead instructions in .claude/agents/docs-lead.md - after each teammate reports a
completion run "python3 tools/tasklist.py check". When T-007 is done, write
docs/api/lead-report.md. Do not document modules yourself.
```
In a second terminal, watch the list evolve:
```bash
watch -n 2 python3 tools/tasklist.py show
```
What to observe:
- T-001…T-005 are claimed in parallel; T-006 stays unclaimable until all five are `done`.
- A teammate that gets `NONE` while T-006 is blocked reports and stops (or, with the
  demo-15 TeammateIdle gate, is sent back to wait for work).
- `done` refuses when the artifact is missing – the tool enforces "no output, no done".

> `.claude/settings.json` pre-approves `Bash(python3 tools/tasklist.py *)` and writes
> under `docs/api/`, and **denies `Edit(./tasks.md)`** – so teammates *cannot* hand-edit
> the list even if they try. The tool is the only write path (it writes via Python, not
> the Edit tool). Teammate permission prompts surface in the lead, so pre-approval
> keeps the team moving.

## Hand-authored vs platform-managed (Lesson 4.4.5)

Run the same work with the **platform** task list for comparison:
```text
Create an agent team to document every module in src/ into docs/api/<module>.md, then an
index page that depends on all of them, then a review task that depends on the index.
Use two doc-writer teammates. Use the shared task list with dependencies.
```
Press `Ctrl+T` to see the platform list. It has built-in dependencies and file-locked
claiming; you trade *control over structure and artifact paths* for *less setup*.

| | Hand-authored `tasks.md` | Platform-managed (TaskCreate/TaskUpdate) |
|---|---|---|
| Who creates rows | you, before launch | the lead, from your prompt |
| Artifact paths | fixed and reviewable | whatever the lead decides |
| Claim safety | only as good as your tooling (lock it!) | file locking built in |
| Visible in git | yes | no (`~/.claude/tasks/`) |

## Practice (after class)

1. Add a `priority` column and make `claim-next` pick the highest-priority eligible task.
2. Add a `stale` check: claimed for more than N minutes (store `claimed_at`). Wire it to
   the lead's instructions for force-reassignment.
3. Task granularity (4.9.2): merge T-004 and T-005 into one task. Does throughput change?
