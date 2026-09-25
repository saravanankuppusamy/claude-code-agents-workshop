# Demo 13 – Your first agent team: enable, spawn, observe, steer

**Lesson:** 4.2 Tiers, 4.4 Setting Up a Team, 4.5 Display Modes, 4.7.3–4.7.4 Messaging
**Before:** Lab 5 / Lab 6 · **Time:** 20 minutes

## Why this demo

Teams are experimental and their failure modes (flag not set → you silently get
subagents; tmux not available → no panes) eat lab time. This demo gives students a
**pre-flight check**, a **research-only first team** (the docs' recommended starting
point – no code edits, so no file conflicts), and practice steering individual teammates.

## Files

| File | Purpose |
|---|---|
| `check-teams-ready.sh` | reports flag, teammateMode, tmux, JSON validity – read-only |
| `settings-examples/user-settings*.json` | what to merge into `~/.claude/settings.json` |
| `.claude/settings.json` | pre-approves reads and writes to `reviews/` so teammate prompts don't pile up in the lead |
| `.claude/agents/devils-advocate.md` | a subagent definition reused as a teammate type |
| `proposals/gift-cards.md` | a feature proposal with deliberate flaws (weak code generation, no expiry, tight timeline) |
| `prompts.md` | copy-paste spawn and steering prompts |
| `tier-exercise.md` | 7-scenario "which tier?" exercise with answers |

## Setup

```bash
cd module-4-agent-teams/demo-13-first-team
./check-teams-ready.sh
```
Merge `settings-examples/user-settings.json` into `~/.claude/settings.json` if the flag
is missing (don't overwrite existing keys). For split panes: `tmux new -s team` first
and use `"teammateMode": "auto"` or `claude --teammate-mode tmux`.

## Run it

```bash
claude                          # in-process: works in any terminal
```
Paste prompt **A** from `prompts.md`. Then B, C, D.

### What to point out while it runs

| Watch for | Why it matters |
|---|---|
| The agent panel below the prompt lists `ux`, `architect`, `skeptic` | a team formed (not subagents) |
| `Ctrl+T` toggles the shared task list | platform-managed task list (`~/.claude/tasks/<team>/`) |
| Teammates messaging each other ("architect → skeptic") | the difference from parallel subagents |
| Permission prompts appear in the **lead** | pre-approve in settings to avoid a queue |
| The lead starting to write before teammates finish | say *"Wait for your teammates to finish"* |

Expected findings the team should surface: `random.choice` is not cryptographically
secure (use `secrets`); no rate limit on redemption → brute force; concurrent partial
redemptions need an atomic balance update; never-expiring balances are a liability on the
books; four weeks is tight for payments + fraud controls.

## Display modes quick reference

| Mode | How | Use when |
|---|---|---|
| in-process (default) | nothing, or `--teammate-mode in-process` | any terminal, 2–3 teammates |
| auto | `"teammateMode": "auto"` | split panes when inside tmux/iTerm2, else in-process |
| tmux | `--teammate-mode tmux` inside tmux | you want every teammate visible |
| iterm2 | `--teammate-mode iterm2` + `it2` CLI | macOS native panes |

Split panes are not supported in the VS Code integrated terminal.

## Team state on disk (show it – it demystifies the feature)

```bash
ls ~/.claude/teams/  ~/.claude/tasks/
cat ~/.claude/teams/*/config.json | head -40      # members, agent types (don't edit)
```

## Discussion

- Work through `tier-exercise.md` as a class (5 min).
- Token cost scales with teammates. When is a 3-teammate review worth ~3× the tokens?

## Practice (after class)

Re-run prompt A with the lead in **plan mode** (Shift+Tab until "plan") and ask for an
"implementer" teammate. Observe the plan-approval request the teammate sends to the lead.
