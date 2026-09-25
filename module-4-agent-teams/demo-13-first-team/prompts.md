# Copy-paste prompts for demo 13

## A. Design review team (research-only – the recommended first team)

```text
Create an agent team to review proposals/gift-cards.md. Spawn three teammates and name them exactly:
- "ux" – customer and bookseller experience, redemption flow, edge cases
- "architect" – data model, code generation, concurrency of balance updates
- "skeptic" – use the devils-advocate agent type
Each teammate writes to reviews/<name>.md only. Have teammates message each other
when a finding affects another's area. When all three are idle, you (the lead) write
reviews/gift-cards-decision.md: go / no-go, top 5 risks, and what to change.
Wait for your teammates to finish before writing the decision.
```

## B. Talk to one teammate directly (in-process mode)

Use ↑/↓ in the agent panel to select **architect**, press Enter, then type:

```text
Also estimate how many codes an attacker could guess per hour if redemption has no rate limit.
```

Esc returns to the lead. The other teammates did not receive this.

## C. Ask the lead to message the team

```text
Tell every teammate: the launch date has moved two weeks earlier. Re-rank your findings
by what must be fixed before launch.
```

(Check the transcript: current Claude Code sends one message per recipient; the lesson's
`to="all"` broadcast may appear as several direct messages.)

## D. Shut down cleanly

```text
Ask all teammates to shut down.
```

## E. Force a team vs. allowing subagents

If Claude uses plain subagents instead of a team, say explicitly: *"Create an agent
team"* and check the flag with `./check-teams-ready.sh`.
