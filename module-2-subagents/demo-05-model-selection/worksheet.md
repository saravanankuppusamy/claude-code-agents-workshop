# Model selection worksheet (Lesson 2.8)

Fill in one row per subagent you design. The decision is per *task*, not per orchestrator.

| Subagent | Task shape (volume, determinism, reasoning depth) | Cost of a wrong answer | Model | Effort | maxTurns | Why |
|---|---|---|---|---|---|---|
| Scan 10,000 log files for error patterns | very high volume, pattern matching, shallow | low – a human reviews the summary | haiku | low/medium | 10–15 | speed and cost dominate |
| Propose refactoring plan for legacy auth module | low volume, multi-step reasoning, ambiguity | medium – plan is reviewed | sonnet (or opus) | high | 15–20 | needs judgment, not raw depth |
| Review DB migration before prod | low volume, high stakes | high – data loss | opus | high/xhigh | 10 | pay for depth where mistakes are expensive |
| _your agent_ | | | | | | |

**Validate before you switch models** (Lesson 2 reflection Q5): run old and new model on
the same fixed input set, compare against an answer key, then compare time and cost.
This demo's `generate_logs.py` prints exactly such an answer key.
