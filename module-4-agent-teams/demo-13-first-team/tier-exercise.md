# Which tier? (Lesson 4.2 – single subagent vs parallel subagents vs agent team)

For each scenario pick **1 single subagent**, **2 parallel subagents** or **3 agent team**,
and name the deciding question. Answers at the bottom.

1. Summarise the last 500 lines of the build log.
2. Review five independent service files against the same checklist, one report at the end.
3. Refactor an auth module where a finding in the token code changes what the session code must do.
4. Security review of 5 independent modules with no shared interfaces.
5. Debug an intermittent failure with three plausible, independent theories where each
   investigator should try to *disprove* the others.
6. Triage an unknown number of flaky tests discovered as the suite runs.
7. Rename a function used in 40 files.

---
**Answers**
1 → 1 (bounded, sequential). 2 → 2 (partitioned, pre-assignable, collect at end – Lab 5).
3 → 3 (mid-run coordination between workers). 4 → 2 (the lesson's Check Your
Understanding – critical question: *does anyone need to redirect anyone during the run?*
No → parallel subagents). 5 → 3 (inter-teammate debate – Lab 6 / demo 17).
6 → 3 (task count unknown in advance → self-claiming from a shared list).
7 → 1 or main conversation (strictly sequential, same-file edits risk conflicts).
