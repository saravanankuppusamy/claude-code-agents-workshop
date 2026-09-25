#!/usr/bin/env bash
# Helper for the scope-precedence demo. Safe: it backs up any existing user agent.
#   ./scope-demo.sh install-user     copy user-scope/release-notes.md to ~/.claude/agents/
#   ./scope-demo.sh remove-user      remove it again (restoring any backup)
#   ./scope-demo.sh session          launch claude with the session-scoped definition (--agents)
#   ./scope-demo.sh status           show which definitions exist at each scope
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
USER_AGENTS="$HOME/.claude/agents"
TARGET="$USER_AGENTS/release-notes.md"
BACKUP="$TARGET.workshop-backup"

case "${1:-status}" in
  install-user)
    mkdir -p "$USER_AGENTS"
    if [[ -f "$TARGET" && ! -f "$BACKUP" ]]; then cp "$TARGET" "$BACKUP"; echo "backed up existing $TARGET"; fi
    cp "$HERE/user-scope/release-notes.md" "$TARGET"
    echo "installed user-scope release-notes -> $TARGET" ;;
  remove-user)
    rm -f "$TARGET"
    if [[ -f "$BACKUP" ]]; then mv "$BACKUP" "$TARGET"; echo "restored your original $TARGET"; fi
    echo "user-scope release-notes removed" ;;
  session)
    cd "$HERE"
    exec claude --agents "$(cat "$HERE/session-scope/agents.json")" ;;
  status)
    printf "%-9s %s\n" "SESSION" "$HERE/session-scope/agents.json (only when launched with --agents)"
    for f in "$HERE/.claude/agents/release-notes.md" "$TARGET"; do
      if [[ -f "$f" ]]; then printf "%-9s %s  (%s)\n" "$([[ $f == $TARGET ]] && echo USER || echo PROJECT)" "$f" "$(grep '^model:' "$f")"; fi
    done ;;
  *) echo "usage: $0 {install-user|remove-user|session|status}"; exit 1 ;;
esac
