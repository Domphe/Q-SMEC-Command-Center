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

## Related
- Prototype: Niket-Work-Documents/BUSINESS/qsmec-command-center.html
- Spec: Niket-Work-Documents/SPECS/COMMAND_CENTER_APP_SPEC.md
- Sync: Niket/CLAUDE_SYNC.md
- Playbook: Q-SMEC-Orchestration-Engine/Playbook/PLAYBOOK.md
