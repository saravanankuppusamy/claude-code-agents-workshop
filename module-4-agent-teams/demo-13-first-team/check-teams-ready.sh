#!/usr/bin/env bash
# Pre-flight for agent-team demos. Read-only: it only reports.
ok()   { printf "  \033[32mOK\033[0m   %s\n" "$1"; }
no()   { printf "  \033[31mNO\033[0m   %s\n" "$1"; }
info() { printf "  --   %s\n" "$1"; }
echo "Agent teams pre-flight"
if command -v claude >/dev/null; then ok "claude found: $(claude --version 2>/dev/null | head -1)"; else no "claude not on PATH"; fi
flag_env="${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-}"
flag_file=$(grep -hs '"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"' ~/.claude/settings.json .claude/settings.json .claude/settings.local.json 2>/dev/null | head -1)
if [[ "$flag_env" == "1" || "$flag_file" == *'"1"'* ]]; then ok "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 (${flag_env:+shell}${flag_file:+ settings})"
else no "agent teams flag not set - see settings-examples/user-settings.json"; fi
mode=$(grep -hs '"teammateMode"' ~/.claude/settings.json 2>/dev/null | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
info "teammateMode: ${mode:-in-process (default)}"
if command -v tmux >/dev/null; then ok "tmux available ($(tmux -V))"; else info "tmux not installed - split panes unavailable, in-process still works"; fi
if [[ -n "${TMUX:-}" ]]; then ok "inside a tmux session"; else info "not inside tmux (needed for split panes with 'tmux'/'auto' modes)"; fi
[[ "${TERM_PROGRAM:-}" == "vscode" ]] && info "VS Code terminal: split panes not supported here - use in-process"
python3 -c "import json;json.load(open('$HOME/.claude/settings.json'))" 2>/dev/null && ok "~/.claude/settings.json is valid JSON" || info "~/.claude/settings.json missing or invalid JSON"
