# Demo 15 – Quality gates: TeammateIdle, TaskCreated, TaskCompleted

**Lesson:** 4.8 Quality Gates (4.8.1–4.8.6), 4.9.5 "Hook never fires"
**Supports:** Lab 6 (TeammateIdle findings validator) · **Time:** 25 minutes

## Why this demo

Lab 6 builds one TeammateIdle validator. This demo covers the whole gate family, the
three TeammateIdle use cases from the lesson (queue drain, completeness, phase
awareness), and two lessons that save hours in real use:

1. **Log the payload before you trust field names.** The lesson's payloads
   (`teammate_name`, `artifact`, `owner`) differ from current docs (`agent_type`,
   `agent_id`, `task_title`). Every gate here logs the *full* payload to
   `hooks/gate-log.jsonl`, so you learn the real shape on your version in one run.
2. **Test that a gate can pass.** A gate that always exits 2 bounces work forever.
   The "golden artifact" test catches it before production (Lesson 4.8.6 CYU).

## Files

| File | Event | Behaviour |
|---|---|---|
| `.claude/settings.json` | registers all three | TeammateIdle **must** be here, not in frontmatter |
| `hooks/teammate_idle_gate.py` | TeammateIdle | tasks.md mode: claimed → finish it; open eligible → claim next; done → artifact valid. No tasks.md: validate `findings/<name>.md`. Unknown payload → allow (fail open) |
| `hooks/task_created_gate.py` | TaskCreated | title must be `T-###: <what> -> findings/<file>.md` |
| `hooks/task_completed_gate.py` | TaskCompleted | artifact named in title must have all sections and ≥1 finding |
| `hooks/buggy_task_completed_gate.py` | – | looks fine, can never pass |
| `hooks/gates_common.py` | – | payload logging, identity resolution, artifact validation |
| `gates.json` | – | sections, patterns, paths – change policy without editing code |
| `findings/TEMPLATE.md` | – | the contract teammates write to |
| `tests/test_gates.py` | – | 13 tests incl. the golden-artifact test and an `expectedFailure` for the buggy gate |
| `app/` | – | three files with planted security issues to review |

## Part 1 – Tests first (5 min)

```bash
cd module-4-agent-teams/demo-15-quality-gates
python3 -m unittest tests/test_gates.py -v
```
Point at `test_golden_artifact_against_buggy_gate` (expected failure). Read
`buggy_task_completed_gate.py` with the class – can anyone spot the bug in 30 seconds?
(`"## Severity:"` has a colon.) The test found it in 0.03 seconds.

Try the gates by hand:
```bash
export CLAUDE_PROJECT_DIR=$PWD
echo '{"task_title":"Review config"}' | python3 hooks/task_created_gate.py; echo "exit=$?"
cp tests/fixtures/missing-severity.md findings/uploads.md
echo '{"teammate_name":"uploads"}' | python3 hooks/teammate_idle_gate.py; echo "exit=$?"
./reset.sh
```

## Part 2 – Run a gated team (15 min)

```bash
./reset.sh
claude
```
```text
Create an agent team for a security sweep of app/. Create one task per file using EXACTLY
these titles:
  T-001: Review app/config.py for insecure defaults and secrets -> findings/config.md
  T-002: Review app/accounts.py for injection and credential handling -> findings/accounts.md
  T-003: Review app/uploads.py for path handling -> findings/uploads.md
Spawn three teammates using the security-reviewer agent type, named config, accounts and
uploads, one task each. When all tasks are complete, write findings/summary.md ranking all
issues by severity.
```
Then try to break discipline:
```text
Add a task called "double-check everything".
```
TaskCreated rejects it and tells the lead the required form.

Watch the gate log live in a second terminal:
```bash
tail -f hooks/gate-log.jsonl | python3 -c "import sys,json;[print(json.loads(l)['event'],json.loads(l)['decision'],json.loads(l)['reason'][:90]) for l in sys.stdin]"
```
Then open the log and **read one full payload** – note the actual field names on your
version and compare with the lesson's examples.

### Provoke a block

While a teammate works, tell it directly (select it in the agent panel):
```text
Skip the Severity section, it's obvious.
```
When it tries to complete its task, TaskCompleted exits 2 with *"missing section
'## Severity'"*; the teammate adds it and completes. Two log lines show block → allow.

## Where each hook lives (Lesson 4.8.1)

| Hook | Register in | Why |
|---|---|---|
| PreToolUse / PostToolUse | agent frontmatter (or settings) | fires inside one agent's tool loop |
| TaskCreated / TaskCompleted | settings (this demo) – the lesson shows lead frontmatter | fires on the task list; settings is the location that works for every agent |
| TeammateIdle | **settings only** | team coordination layer never reads agent files |

Note: TaskCreated/TaskCompleted fire for the **platform** task list (TaskCreate/TaskUpdate).
A hand-authored `tasks.md` edited with Write/Edit fires none of them – validate those
with TeammateIdle (tasks.md mode) or a PostToolUse hook on edits to `tasks.md`.

## Exit codes (Lesson 4.8.2)

| | 0 | 2 |
|---|---|---|
| TeammateIdle | go idle | stderr → feedback, keep working |
| TaskCreated | create | reject creation, feedback |
| TaskCompleted | complete | refuse completion, feedback |

## Practice (after class)

1. Add use case 3 from the lesson: on successful idle, write `findings/<name>-complete.signal`.
2. Make `gates.json` support per-artifact section lists (e.g. `summary.md` needs `## Ranking`).
3. Point `teammate_idle_gate.py` at demo 14's `tasks.md` and run that team with the gate.
