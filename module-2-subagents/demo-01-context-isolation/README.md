# Demo 01 – Context isolation: what crosses the boundary?

**Lesson:** 2.2 Introduction to Subagents (2.2.3 Key Mechanics, 2.2.5 What Transfers)
**Time:** 10 minutes · **Type:** instructor demo, students can repeat after class

## Why this demo

Students *read* the "what transfers" table in the lesson. This demo lets them *see* it.
A diagnostic subagent (`context-probe`) reports, with evidence, what it can and cannot
see. The single most important takeaway: **the `prompt` string is the only
task-specific channel from the orchestrator to a subagent.**

## Files

| File | Purpose |
|---|---|
| `.claude/agents/context-probe.md` | Haiku agent that reports what is in its context – never guesses |
| `CLAUDE.md` | Contains the marker `HALYARD` so we can test whether CLAUDE.md reaches the subagent |
| `src/pricing.py` | Small file the parent reads so we can test whether parent tool results transfer |

## Run it

```bash
cd module-2-subagents/demo-01-context-isolation
export TIDEWATER_ENV=staging-demo     # environment variable the subagent should inherit
claude
```

### Step 1 – Put information into the *parent* conversation only

```text
Our release codename for this sprint is BLUEFIN. Remember that.
Also read src/pricing.py and tell me the member discount.
```

The parent now "knows" BLUEFIN and has a Read tool result in its history.

### Step 2 – Delegate with a thin prompt

```text
Use the context-probe subagent. Tell it only: "Run your probe report."
```

**Expected** (exact wording varies):

| Item | Expected | Why |
|---|---|---|
| Release codename | `NOT VISIBLE` | Parent conversation history does not transfer |
| TIDEWATER_ENV | `staging-demo` | Environment is inherited from the parent process |
| Working directory | the demo folder | Inherited |
| Parent tool results | `NONE` | Tool results do not transfer |
| CLAUDE.md codeword | **Observe and discuss** – see note below | |

### Step 3 – Delegate with a *complete* prompt

```text
Use the context-probe subagent. In your prompt to it, include the release codename
and the member discount you found, then ask it to run its probe report.
```

Now items 1 and 2 show the values – because the orchestrator serialised them into
the prompt. This is the design rule from 2.2.5: *every piece of context the subagent
needs must be written into `prompt`.*

### Step 4 (optional) – Look at the actual Agent call

Press `Ctrl+O` (transcript view) and find the `Agent(...)` tool call. Point out the
`subagent_type` and `prompt` fields – the prompt is the whole briefing.

## Note on CLAUDE.md (discussion point)

Lab 2 describes CLAUDE.md as influencing subagents mainly *through the orchestrator*.
Current docs list an `omitClaudeMd: true` subagent field, which implies subagents load
CLAUDE.md by default. **Observed on Claude Code 2.1.282:** the probe reports
`HALYARD` for item 3 – CLAUDE.md content *is* in the subagent's context. Run it on your
version and compare – a good "trust observation over folklore" moment. Then add
`omitClaudeMd: true` to the probe's frontmatter, restart, and re-run.

Reference run (2.1.282, abbreviated):

```text
1. Delegation prompt I received (verbatim): "Run your probe report."
2. Release codename mentioned in the parent conversation: NOT VISIBLE
3. Project codeword from CLAUDE.md: HALYARD   (present in my context)
4. TIDEWATER_ENV: staging-demo
7. Anything from the parent's earlier tool results I can see: NONE
```

> Self-reports are evidence, not proof. To *verify* what a subagent saw, open its
> transcript: `~/.claude/projects/<project-path>/<session-id>/subagents/agent-*.jsonl`.

## Discussion questions

1. The subagent inherited `TIDEWATER_ENV`. What does that mean for secrets in your
   shell environment? (Isolation is *context* isolation, not a security sandbox – Lesson 3.2.)
2. Rewrite this weak delegation prompt so it is self-contained:
   `"Check the pricing thing we talked about."`
3. Why does the orchestrator only get the subagent's *final* message back, and why is
   that a feature?

## Practice (after class)

Write a second probe, `context-probe-strict`, that is allowed only `Read` and has
`omitClaudeMd: true`. Predict its report before running it, then check your prediction.
