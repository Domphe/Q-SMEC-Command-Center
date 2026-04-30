# CLAUDE.md — Q-SMEC Command Center

## What This Is
Full-stack web app (FastAPI + React) serving as NIKET NA LLC's unified operational hub.
7 tabs: Overview, Email Triage, Clients & Partners, Pipeline, Repos, Notes, Command Center.

## Stack
- Backend: FastAPI + SQLModel + SQLite
- Frontend: React 18 + Vite + Tailwind CSS
- APIs: Gmail, GitHub, Anthropic, Google Gemini

## Code Rules
- No f-strings — use .format() (ecosystem standard)
- Never commit .env or token.json
- All API calls via services/ (never direct in routers)
- Bridge files export to bridge/ directory

## Key Commands
- Dev: cd backend && uvicorn main:app --reload
- Frontend dev: cd frontend && npm run dev
- Build: cd frontend && npm run build (output -> backend/static/)
- DB init: python -c "from backend.database import init_db; init_db()"

## Dependency Management

- **Source of truth**: `pyproject.toml`
- **Lock file**: `uv.lock` — regenerate with `uv lock` after any dep change
- **Validation**: `deptry .` before committing
- **Package mapping**: `import dotenv` → `python-dotenv`
- **Runtime deps**: uvicorn is the ASGI server — flagged as "unused" by deptry but required at runtime. Excluded via `[tool.deptry.per_rule_ignores] DEP002`
- **Local modules**: backend, client, email_cache, note, pipeline, task excluded via DEP001 ignores
- **Audit baseline**: `E:/Data1/Niket-Work-Documents/AUDITS/env-audit-reports/Q-SMEC-Command-Center_audit.json`

## Related
- Prototype: Niket-Work-Documents/BUSINESS/qsmec-command-center.html
- Spec: Niket-Work-Documents/SPECS/COMMAND_CENTER_APP_SPEC.md
- Sync: Niket/CLAUDE_SYNC.md
- Playbook: Q-SMEC-Orchestration-Engine/Playbook/PLAYBOOK.md


---

## Standing Rule R57 — Folder Migration Preflight (CROSS-CUTTING, 2026-04-29)

Before any folder operation that triggers per the conditions in [`Q-SMEC-Claude/shared-memory/protocol_folder_migration_preflight.md`](../Q-SMEC-Claude/shared-memory/protocol_folder_migration_preflight.md) (>5 file deletes, >10 file moves crossing folders, top-level dir delete, ANY operation described as "consolidation" / "migration" / "cleanup" / "merge X into Y", crossing repo boundaries, external drives), run:

```bash
python3 /mnt/e/Data1/Q-SMEC-Claude/agents/folder_migration_preflight_agent.py scan PLAN.json
```

The agent runs **six universal checks** (SHA256 dup-verify, real-diff stale-verify, canonical-existence proof, junction safety, 30-day quarantine archive, sole-author check) plus **content-class checks** routed by destination class. On verdict `PASS` the agent writes `.preflight_passed.json` (24-hour TTL). The Claude Code `PreToolUse` hook BLOCKS `rm -rf` / `Remove-Item -Recurse` / `fsutil reparsepoint delete` outside the cache/build allowlist unless the marker is current. Per-repo `.githooks/pre-commit` rejects commits with recursive deletes lacking a referenced preflight report.

**Critical:** filename + size + date is **not** proof of duplicate (only SHA256 bit-identity is). Newer-date-wins is **not** proof of stale (only diff-fully-subsumed is). "Doesn't exist in canonical" must be proven by listing canonical roots, not asserted.

Authoritative rule: `Q-SMEC-Claude/CLAUDE.md` §R57. Canonical protocol: `Q-SMEC-Claude/shared-memory/protocol_folder_migration_preflight.md`.
