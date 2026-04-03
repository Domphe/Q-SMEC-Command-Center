"""Q-SMEC Command Center — FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import init_db
from backend.seed import seed_if_empty
from backend.routers import overview, emails, clients, pipeline, repos, notes, ai_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and seed data on startup."""
    init_db()
    seed_if_empty()
    yield


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
    return {"status": "ok", "version": "2.0.0", "app": "Q-SMEC Command Center"}


# Serve built frontend from backend/static if it exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir) and os.listdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
