"""Q-SMEC Command Center — FastAPI application entry point."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import init_db
from backend.seed import seed_if_empty
from backend.routers import (
    overview, emails, clients, pipeline,
    notes, ai_router, agent,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# APScheduler — optional, only if running in production
_scheduler = None


def _start_scheduler():
    """Start background job scheduler."""
    global _scheduler
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from backend.jobs.email_sync import run_email_sync
        from backend.jobs.note_export import run_note_export
        from backend.jobs.agent_digest import (
            run_agent_digest, run_morning_brief,
        )

        _scheduler = BackgroundScheduler()
        _scheduler.add_job(
            run_email_sync, "interval",
            minutes=15, id="email_sync",
        )
        _scheduler.add_job(
            run_note_export, "interval",
            minutes=5, id="note_export",
        )
        _scheduler.add_job(
            run_agent_digest, "interval",
            minutes=30, id="agent_digest",
        )
        _scheduler.add_job(
            run_morning_brief, "cron",
            hour=7, minute=0, id="morning_brief",
        )
        _scheduler.start()
        logger.info(
            "Scheduler started "
            "(email:15m, notes:5m, digest:30m, "
            "brief:7am)"
        )
    except Exception as e:
        logger.warning("Scheduler not started: %s", e)


def _run_migrations():
    """Add new columns safely — no-op if they already exist."""
    from backend.database import engine
    import sqlalchemy as sa
    with engine.connect() as conn:
        for stmt in [
            "ALTER TABLE email_cache "
            "ADD COLUMN urgency TEXT DEFAULT 'review'",
            "ALTER TABLE email_cache "
            "ADD COLUMN confidence REAL DEFAULT 0.5",
        ]:
            try:
                conn.execute(sa.text(stmt))
                conn.commit()
            except Exception:
                conn.rollback()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database, seed data, and start scheduler on startup."""
    init_db()
    _run_migrations()
    seed_if_empty()
    _start_scheduler()
    yield
    if _scheduler:
        _scheduler.shutdown(wait=False)
        logger.info("Background scheduler stopped")


_is_debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

app = FastAPI(
    title="Q-SMEC Command Center",
    version="2.0.0",
    description="Unified operational hub for NIKET NA LLC's 18-repo Q-SMEC ecosystem",
    lifespan=lifespan,
    docs_url="/docs" if _is_debug else None,
    redoc_url="/redoc" if _is_debug else None,
)

# CORS — configurable via CORS_ORIGINS env var (comma-separated)
_default_origins = "http://localhost:5173,http://localhost:8000,http://niket-hv-01:8000"
_cors_origins = [
    o.strip() for o in os.getenv("CORS_ORIGINS", _default_origins).split(",") if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# API routers
app.include_router(overview.router, prefix="/api", tags=["overview"])
app.include_router(emails.router, prefix="/api/emails", tags=["emails"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["pipeline"])
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
app.include_router(
    ai_router.router, prefix="/api/ai", tags=["ai"],
)
app.include_router(
    agent.router, prefix="/api/agent", tags=["agent"],
)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "version": "2.0.0",
        "app": "Q-SMEC Command Center",
        "scheduler": _scheduler is not None and _scheduler.running if _scheduler else False,
    }


# Serve built frontend from backend/static if it exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir) and os.listdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
