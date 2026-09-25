# Demo 09 – Hooks: a guard that can't be argued with, and an audit trail

**Lesson:** 3.6 Lifecycle Hooks, 3.7 Conditional Validation with Hooks
**Supports:** Lab 4 core + Challenges 1–3 (reference solutions) · **Time:** 30 minutes

## Why this demo

Lab 4 builds the lesson's substring keyword guard. This demo starts there, **breaks it
in front of the class** (false positives *and* false negatives), then shows a
production-minded guard, input rewriting with `updatedInput`, a structured audit log,
a rate limiter and per-agent policies. Every hook ships with tests you can run without
Claude.

## Files

| File | Event | What it demonstrates |
|---|---|---|
| `hooks/naive_guard.py` | PreToolUse | Lesson/Lab 4 version – substring match, exit 2 |
| `hooks/sql_guard.py` | PreToolUse | whole-word matching after stripping literals, statement splitting, table allowlist, dot-command allowlist, fail-closed on pipes/redirects, JSON `deny` with reason |
| `hooks/enforce_limit.py` | PreToolUse | `updatedInput` – rewrites unbounded SELECTs to add `LIMIT` |
| `hooks/rate_limit.py` | PreToolUse | Lab 4 Challenge 2 – rolling window, file state + `fcntl` lock |
| `hooks/audit_log.py` | PostToolUse | JSONL audit with agent, duration, result preview (`tool_response`) |
| `policies/ops.json`, `policies/marketing.json` | – | Lab 4 Challenge 1 reflection: *configurable* allowlist per agent, no script edits |
| `.claude/agents/ops-analyst.md` | – | guard + rate limit + audit (with `if:`) |
| `.claude/agents/ops-analyst-naive.md` | – | naive guard for the comparison |
| `.claude/agents/catalogue-analyst.md` | – | rewrite hook + narrower policy |
| `tests/test_hooks.py` | – | 25 guard cases + naive failures + rewrite + audit + rate limit |
| `setup_db.py`, `reset.sh` | – | builds `db/tidewater.db` with deliberate traps |

The database contains traps for naive guards: a `books.drop_date` column, a book titled
*Delete Me Not: A Memoir*, and a sensitive `staff_payroll` table.

## Before class

```bash
cd module-3-advanced-patterns/demo-09-hooks-guard-and-audit
./reset.sh                                   # build db/tidewater.db
python3 -m unittest tests/test_hooks.py -v   # all green
which sqlite3 || sudo apt-get install -y sqlite3
```

## Part 1 – Test before wiring (3 min)

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"sqlite3 db/tidewater.db \"DROP TABLE books\""}}' \
  | python3 hooks/naive_guard.py; echo "exit=$?"            # exit=2, BLOCKED on stderr

echo '{"tool_name":"Bash","tool_input":{"command":"sqlite3 db/tidewater.db \"DROP TABLE books\""}}' \
  | python3 hooks/sql_guard.py --policy policies/ops.json; echo "exit=$?"   # exit=0 + JSON deny
```
Point out the two blocking styles: **exit 2 + stderr** vs **exit 0 + JSON
`permissionDecision: "deny"` + reason**. Never mix them – JSON is ignored on exit 2.

## Part 2 – Break the naive guard (7 min)

```bash
claude
```
```text
Use the ops-analyst-naive subagent to list the titles and drop_date of books leaving the catalogue.
```
Blocked – `drop_date` contains `DROP`. (False positive.)
```text
Use the ops-analyst-naive subagent to find the price of 'Delete Me Not: A Memoir'.
```
Blocked again – string literal. Now the dangerous one:
```text
Use the ops-analyst-naive subagent to run: UPDATE books SET price = 0
```
**Allowed** – `UPDATE` isn't in the list. (False negative.) Run `./reset.sh` afterwards.
The naive guard is simultaneously too strict and too loose.

## Part 3 – The production-minded guard (10 min)

```text
Use the ops-analyst subagent to list the titles and drop_date of books leaving the catalogue.
Use the ops-analyst subagent to find the price of 'Delete Me Not: A Memoir'.
Use the ops-analyst subagent to run: UPDATE books SET price = 0
Use the ops-analyst subagent to show the average salary in staff_payroll.
Use the ops-analyst subagent to run: SELECT 1 FROM books; DROP TABLE books
```
Expected: allow, allow, deny, deny (table allowlist), deny (smuggled statement). Each
denial arrives with a **reason the agent can read** – watch it explain rather than retry.

Then the audit trail:
```bash
tail -n 5 audit/query-audit.jsonl | python3 -m json.tool --json-lines
```
Only executed commands appear – blocked calls never reach PostToolUse.

## Part 4 – Rewriting input with `updatedInput` (5 min)

```text
Use the catalogue-analyst subagent to list every book title and price.
```
The agent asked for all rows; the hook silently appended `LIMIT 50`. Discuss: rewriting
is powerful and invisible – log it, and remember `"permissionDecision": "allow"` also
skips the permission prompt for that call.

## Part 5 – `if:` vs `matcher:` (5 min, Lab 4 Challenge 3)

In `ops-analyst.md` the **audit** hook has `if: "Bash(sqlite3 *)"` so no Python process
is spawned for `ls` or `cat`. The **guard** deliberately has *no* `if:`.

> Design rule: use `if:` to skip *expensive, non-security* hooks. Keep *security* hooks
> broad and let the script decide – a guard that is never invoked cannot fail closed.

(Current docs place `if` on the individual hook handler, as here; Lab 4 shows it at
the matcher level. If one form is ignored on your version, try the other and note it.)

## What the linter says (and why it's right)

`python3 ../../tools/lint_agents.py .claude/agents` warns that `ops-analyst` "describes
itself as read-only but can call Bash". True: `sql_guard.py` only inspects `sqlite3`.
`echo hi > notes.txt` would still run. Fix with `permissions.deny` rules in
`.claude/settings.json`, a second hook, or by removing Bash in favour of an MCP query
tool. Defence in depth.

## Known limits of `sql_guard.py` (discussion)

- It is a regex-level SQL reader, not a parser. For production use a real parser
  (e.g. `sqlglot`) or – better – a **read-only database user**. The hook is one layer.
- A view named on the allowlist could expose a sensitive table. Policy must cover views.
- Rate-limit state is per agent type; parallel instances of the same agent share a budget.

## Practice (after class)

1. Add a test case to `tests/test_hooks.py` that defeats `sql_guard.py`, then fix the guard.
2. Add `"deny_columns": ["email"]` to `policies/ops.json` and implement it.
3. Write a `PostToolUse` hook that warns the model when a result exceeds 200 lines.
   The lesson says hook stdout replaces the output the model sees; current docs describe
   returning `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "..."}}`.
   Try both on your version and note which one the model actually receives.
