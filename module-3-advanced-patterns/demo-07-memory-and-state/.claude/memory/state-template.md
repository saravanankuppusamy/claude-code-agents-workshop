<!-- Schema v2 for file-backed agent state. Every session entry MUST use exactly
     these fields, in this order. Tools: tools/validate_state.py checks conformance. -->
## Session {{YYYY-MM-DD}} {{HH:MM}}

- **date:** {{ISO-8601 date}}
- **agent:** {{agent name}}
- **files_examined:** {{comma-separated repo-relative paths}}
- **work_completed:** {{one or two sentences}}
- **decisions:**
  - {{decision}}
- **open_questions:**
  - {{question, or "none"}}
<!-- end-session -->
