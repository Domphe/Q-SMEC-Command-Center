"""Q-SMEC Command Center — FastAPI application entry point."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import init_db
from backend.seed import seed_if_empty
from backend.routers import overview, emails, clients, pipeline, repos, notes, ai_router

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
        from backend.jobs.repo_health import run_repo_health_check
        from backend.jobs.note_export import run_note_export

        _scheduler = BackgroundScheduler()
        _scheduler.add_job(run_email_sync, "interval", minutes=15, id="email_sync")
        _scheduler.add_job(run_repo_health_check, "interval", hours=1, id="repo_health")
        _scheduler.add_job(run_note_export, "interval", minutes=5, id="note_export")
        _scheduler.start()
        logger.info("Background scheduler started (email:15m, repos:1h, notes:5m)")
    except Exception as e:
        logger.warning("Scheduler not started: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database, seed data, and start scheduler on startup."""
    init_db()
    seed_if_empty()
    _start_scheduler()
    yield
    if _scheduler:
        _scheduler.shutdown(wait=False)
        logger.info("Background scheduler stopped")


app = FastAPI(
    title="Q-SMEC Command Center",
    version="2.0.0",
    description="Unified operational hub for NIKET NA LLC's 18-repo Q-SMEC ecosystem",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000", "http://niket-hv-01:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(overview.router, prefix="/api", tags=["overview"])
app.include_router(emails.router, prefix="/api/emails", tags=["emails"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["pipeline"])
app.include_router(repos.router, prefix="/api/repos", tags=["repos"])
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
app.include_router(ai_router.router, prefix="/api/ai", tags=["ai"])


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
