# Choosing a good `maxTurns` value

`maxTurns` is a circuit breaker, not a target. A good value lets a normal run finish
with some room to spare and stops a stuck agent before it burns much money.
`tools/lint_agents.py` warns when an agent leaves it out.

## What counts as a turn

One turn is one model response plus the tool results that come back to it. If the
agent makes several tool calls in parallel in one response, that is still one turn.
So the number tracks how many rounds of "think, call tools, read results" the task
needs, not how many files it touches.

## How to pick the number

1. **Estimate the normal path.** List the steps the agent should take. Take a reviewer
   that greps for candidates, reads 2–3 files and writes a report: about 1 + 2–3 + 1,
   so roughly 5 turns. Add 1 for the final answer.
2. **Add headroom of about 1.5–2×.** That covers a retry after a failed tool call, one
   extra file read, or a clarifying search. A 5-turn task becomes `maxTurns: 8`.
3. **Check it with real runs.** Run the agent on 3–5 typical inputs and note how many
   turns each one used. Set the limit a little above the highest count you see.
4. **Tune it from what happens.**
   - **Too low:** the agent stops partway, with no final report or a half-written file.
     Before raising the limit, check whether a tighter prompt would fix it, such as
     "use Grep first, don't read every file". The practice question in
     [demo 05](../module-2-subagents/demo-05-model-selection/README.md) asks exactly this.
   - **Too high:** you rarely notice until the agent loops, for example re-running a
     failing command over and over. Then you pay for every turn up to the limit.

## Other factors

- **Model:** smaller models such as haiku often need a few more turns to do the same
  task, because they explore more and recover from mistakes less well. That's why the
  three log-triage agents in demo 05 all use the same 12, so the model comparison is fair.
- **Tool access:** a narrow tool allowlist and a clear output format shrink the number
  of turns the agent needs.
- **Cost of running out:** a background or long-running agent can get a much higher
  limit. In this repo, `review-indexer` (demo 10) is set to 60 and the agent-team
  members in demo 14 are set to 30.

## Values used in this repo

| Task shape | `maxTurns` |
|---|---|
| Narrow, predictable (extract, check CI, config audit) | 4–6 |
| Read a few files and write one output (reviewer, triager) | 8–10 |
| Investigation or open-ended analysis (log triage, devil's advocate) | 12 |
| Agent-team members / security review | 20–30 |
| Long background indexing | 60 |

## Rule of thumb

Count the turns a normal run needs, double it, then check against real runs. Record
the observed turn counts in the `maxTurns` column of the
[demo 05 worksheet](../module-2-subagents/demo-05-model-selection/worksheet.md).
