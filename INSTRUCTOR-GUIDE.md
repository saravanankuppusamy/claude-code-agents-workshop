# Instructor guide – WA3877 Advanced Claude Code with Agents (1 day)

How to use this repository alongside the Lesson Guide and Lab Guide. The labs stay the
hands-on backbone; demos are short, instructor-driven moments that make a concept
*visible* right before students need it, plus reference solutions for lab challenges.

## Pre-class checklist (the day before)

- [ ] `claude --version` on the lab image; skim `docs/version-notes.md` and try items 1, 2, 4 on that version
- [ ] Clone this repo on the instructor machine; `./run-tests.sh` → all green
- [ ] **Launch `claude` once from the repo root and accept the folder-trust prompt** (hooks won't fire otherwise)
- [ ] `module-4-agent-teams/demo-13-first-team/check-teams-ready.sh` → flag set, tmux present
- [ ] `sqlite3 --version` (demo 09 / Lab 4)
- [ ] Run `./reset.sh` in demos 07, 09, 10, 14, 15, 17
- [ ] Font size up, terminal ≥ 120 columns for split panes
- [ ] Decide which demos are **core** vs **optional** for your pace (table below)

## Run of show (09:00–17:00)

| Time | Block | Demo(s) | Lab | Core / optional |
|---|---|---|---|---|
| 09:00 | Lesson 1 intro, environment check | – | – | |
| 09:15 | **Lesson 2.1–2.4** What a subagent is, built-ins, creating | **01** context isolation (10) · 02 built-in vs custom (5, optional) | | 01 core |
| 09:45 | **Lesson 2.6–2.7** Frontmatter, allow/deny | **03** denylist leak + linter (12) | **Lab 1** (30) | core |
| 10:30 | Break | | | |
| 10:45 | **Lesson 2.5, 2.8** Scope, models | **04** scope precedence (10) · 05 model selection (10, run in parallel while you talk) | **Lab 2** (40) | 04 core, 05 optional |
| 11:50 | **Lesson 3.2–3.3** Execution model, permission modes | **06** Round 4 only – the control stack (10) | | core |
| 12:05 | **Lesson 3.4–3.5** Memory, skills | **07** Parts A+B (10) · **08** Rounds 1–2 (8) | | core |
| 12:30 | Lunch | | | |
| 13:15 | | | **Lab 3** (40) | |
| 13:55 | **Lesson 3.6–3.7** Hooks | **09** Parts 1–3 (15) | **Lab 4** (40) | core |
| 14:50 | Break | | | |
| 15:00 | **Lesson 3.8–3.10** Background, chains, parallel | 12 Part 2 noisy ops (5) · 10, 11 (optional) | | optional |
| 15:10 | **Lesson 4.2–4.5** Tiers, team setup, display | **13** pre-flight + design team (10) · tier exercise (5) | **Lab 5** (30) | core |
| 16:00 | **Lesson 4.6–4.8** Task lists, gates | **14** Parts 1–2 race demo (5) · **15** Part 1 golden-artifact test (5) | **Lab 6** (core only) | core |
| 16:45 | Wrap-up: demo 17 debrief (answer-key table only), Q&A, after-class path | 17 (table) | | |

Running late? Cut in this order: 02, 05, 10, 11, 12, then 16 (point to it for Lab 6
Challenge 1). Never cut 03, 09 or 14 Part 1 – they are the "aha" moments.

Running early? Run demo 17 live (30 min) in place of Lab 6 Challenge 2, or 16 as a
lead-in to Lab 6 Challenge 1.

## Demo notes (what must land, what goes wrong)

| Demo | The moment that must land | Likely live failure → recovery |
|---|---|---|
| 01 | `NOT VISIBLE` for the codename while `TIDEWATER_ENV` *is* visible | Claude passes the codename anyway → you said more than "Run your probe report"; redo with the exact wording |
| 03 | `git diff` showing the denylist reviewer changed the file via `sed` | Model refuses to try Bash → prompt: "you may use any tool available to you" |
| 04 | `scope=PROJECT` → `scope=SESSION` → `scope=USER` in three runs | Stale user agent from a previous class → `./scope-demo.sh status`; **always `remove-user` after** |
| 06 | Hook denial reason "may only write under out/" | Hook doesn't fire → folder not trusted / relaunch |
| 07 | State survives restart; validator flags the truncated fixture | Agent paraphrases decisions → point at "quote them" in its protocol |
| 08 | One edit to SKILL.md changes two agents | Forgot to relaunch after editing – skills load at start |
| 09 | Naive guard blocks `drop_date` but allows `UPDATE` | `sqlite3` missing → `apt install sqlite3`; tests still demo the logic |
| 13 | Teammates messaging each other in the panel | Got subagents → flag not set → `check-teams-ready.sh` |
| 14 | `race_demo.py naive` – 8 owners for T-001 | none (no Claude involved) |
| 15 | `expectedFailure` test catching the buggy gate | none (no Claude involved) |
| 17 | `--serial` run: negative stock with zero concurrency | Lead anchors on race anyway → show the experiment table; that *is* the lesson |

## Mapping: Lab Guide challenges → reference material here

| Lab challenge | Reference |
|---|---|
| Lab 1 next steps (user scope) | demo 04 |
| Lab 2 Ch. 1 (distinct names) | demo 04 discussion Q3 |
| Lab 2 Ch. 2 (`--agent`, CLI scope) | demo 04 Round 4 + `session-scope/agents.json` for `--agents` |
| Lab 3 Ch. 1 (structured schema) | demo 07 `state-template.md`, `validate_state.py`, `prune_state.py` |
| Lab 3 Ch. 2 (commit-standards skill) | demo 08 `commit-standards/` with validator script |
| Lab 3 next steps (SubagentStop) | demo 07 Part C |
| Lab 4 Ch. 1 (table allowlist) | demo 09 `sql_guard.py` + `policies/*.json` |
| Lab 4 Ch. 2 (rate limit) | demo 09 `rate_limit.py` (with `fcntl` lock) |
| Lab 4 Ch. 3 (`if:`) | demo 09 `ops-analyst.md` PostToolUse handler |
| Lab 5 Ch. 1 (security reviewer) | demo 15 (`security-reviewer` + gates) |
| Lab 6 Ch. 1 (hypothesis-c, rubric, custom command) | demo 16 (skill), demo 17 (rubric) |
| Lab 6 Ch. 2 (escalation) | demo 17 practice item 2 |
| Lab 6 next steps (TaskCompleted) | demo 15 |

## Answers to lesson "Check Your Understanding" prompts (quick reference)

- **2.2.4 Why a second session?** Isolation (context, errors, noisy output), specialisation (tools, prompt, model), parallelism. Demo 01, 12.
- **2.8.5 Three subagents:** logs → Haiku; refactor plan → Sonnet (Opus if very gnarly); prod migration review → Opus. Demo 05 `worksheet.md`.
- **3.3.5 bypassPermissions for CI?** Which tools, which hooks (tested?), is the runner sandboxed, would `dontAsk` + pre-approved commands do? Demo 06.
- **3.5.5 Shared naming rules?** In a skill. Demo 08.
- **3.7.4 DROP blocked with exit 2 – next?** Tool doesn't run; stderr goes to the model, which usually explains or tries a different approach; PostToolUse does **not** fire. Demo 09 audit log proves it.
- **4.2.3 Five independent modules?** Parallel subagents – the critical question is whether anyone must redirect anyone mid-run. Demo 13 `tier-exercise.md`.
- **4.6.3 Simultaneous claims?** File shows only the last writer; the check must find duplicate claims/owners – better to prevent with a locked claim. Demo 14.
- **4.8.6 Gate always exits 2?** Infinite bounce; catch with a golden-artifact test before production. Demo 15.

## Safety reminders for a live room

- `--dangerously-skip-permissions` only in disposable lab VMs; say so every time you use it.
- Demo 04 writes to `~/.claude/agents/` – clean up.
- Demo 09's naive agent can really run `UPDATE` – `./reset.sh` afterwards.
