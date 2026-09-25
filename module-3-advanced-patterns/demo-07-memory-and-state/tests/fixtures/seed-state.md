# project-state.md – file-backed state for session-tracker
<!-- Plain Markdown. Claude Code does not manage this file. You own it. -->

## Session 2026-09-18 10:05

- **date:** 2026-09-18
- **agent:** session-tracker
- **files_examined:** src/search.py
- **work_completed:** Reviewed ISBN normalisation; it strips hyphens but does not validate check digits.
- **decisions:**
  - Keep normalise_isbn pure; add a separate validate_isbn function.
- **open_questions:**
  - Should ISBN-10 be converted to ISBN-13 before comparison?
<!-- end-session -->
