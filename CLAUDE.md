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
