# Q-SMEC Command Center — AI Tool Bridge

This directory contains JSON files that AI tools (Claude Code, Cowork, Project) read to pick up tasks and state from the Command Center.

## Files

- `pending_notes.json` — Notes tagged ACTION with status=pending, for AI tools to execute
- `command_center_state.json` — Current KPIs, pipeline status snapshot
- `email_digest.json` — Latest email triage results

## How AI Tools Read These

- **Claude Code:** Reads on session startup via hooks
- **Claude Cowork:** COWORK_INSTRUCTIONS.md references bridge/ at session start
- **Claude Project:** Has memory instruction to check bridge files when referenced

## Schema

All files follow the schemas defined in the spec:
`Niket-Work-Documents/SPECS/COMMAND_CENTER_APP_SPEC.md` (Section 7)
