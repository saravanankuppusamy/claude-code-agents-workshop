# Module 4 – Orchestrating Agent Teams

Companion demos for **Lesson 4** of WA3877 and **Labs 5–6**.

> Agent teams are experimental. Enable with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
> (settings `env` block or shell). Run `demo-13-first-team/check-teams-ready.sh` first.

| Demo | Lesson section | Pairs with | What students see |
|---|---|---|---|
| [13 – First team](demo-13-first-team/) | 4.2, 4.4, 4.5, 4.7.3–4 | before Lab 5 | pre-flight, research-only design-review team, steering teammates, tier exercise |
| [14 – Hand-authored task list](demo-14-hand-authored-tasklist/) | 4.4.3–4.6 | Lab 6 | the claim race *happening*, then prevented with a locked claim tool; `check` for 7 kinds of task-list rot |
| [15 – Quality gates](demo-15-quality-gates/) | 4.8 | Lab 6 | TeammateIdle + TaskCreated + TaskCompleted, payload logging, golden-artifact test |
| [16 – Spawn prompt as skill](demo-16-spawn-prompt-as-skill/) | 4.7.1–4.7.2 | Lab 6 Ch. 1 | `/release-check <version>` with gates and stop conditions; skill vs command |
| [17 – Competing hypotheses](demo-17-competing-hypotheses/) | 4.3 | Lab 6 | adversarial debate + reproducers overturns the "obvious" race-condition answer |

## Team design checklist

- [ ] Could parallel subagents do this? (No mid-run coordination → yes → don't build a team.)
- [ ] 2–4 teammates; one artifact per task; one writer per artifact
- [ ] Teammate types are committed agent definitions (tools + model + protocol)
- [ ] Spawn prompt names agents, **checkable gates**, and **stop conditions** – stored as a skill
- [ ] Permissions pre-approved (teammate prompts surface in the lead)
- [ ] TeammateIdle in `settings.json`; gates tested with a golden artifact
- [ ] Every hook logs its payload on first run
