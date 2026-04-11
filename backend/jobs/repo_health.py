"""Background job: check GitHub repo health every hour."""

import logging
import threading

from backend.services.github_service import is_github_configured, get_repo_info

logger = logging.getLogger(__name__)

# The 18 repos to check
REPO_NAMES = [
    "Q-SMEC-Orchestration-Engine", "Q-SMEC-Orchestration-Docs",
    "NIKET-Q-SMEC-Product", "Q-SMEC-Quantum-Tools",
    "Q-SMEC-Quantum-Tools-Docs", "Q-SMEC-Client-Databases",
    "Q-SMEC-Client-Databases-Docs", "Q-SMEC-Testing-Workflow-Sequence",
    "Q-SMEC-Testing-Workflow-Docs", "Niket-Work-Documents",
    "Computer-Infrastructure-Docs", "Q-SMEC-Agentic-AI-Tools",
    "Q-SMEC-MCP-Server", "Q-SMEC-Materials-Database",
    "Q-SMEC-EW-Sensor-Models", "Q-SMEC-ML-Potentials",
    "Q-SMEC-Benchmarks", "Q-SMEC-Publications",
]

# Cache for last health check results — guarded by lock
_last_health = {}
_health_lock = threading.Lock()


def run_repo_health_check():
    """Check health of all repos via GitHub API."""
    global _last_health

    if not is_github_configured():
        logger.debug("GitHub not configured — skipping repo health check")
        return

    logger.info("Starting repo health check...")
    results = {}
    for name in REPO_NAMES:
        try:
            info = get_repo_info(name)
            if info:
                results[name] = info
        except Exception as e:
            logger.warning("Failed to check %s: %s", name, e)
            results[name] = {"name": name, "health": "error", "error": str(e)}

    with _health_lock:
        _last_health = results
    logger.info("Repo health check complete: %d/%d repos checked", len(results), len(REPO_NAMES))


def get_cached_health() -> dict:
    """Return cached health results (empty if no check has run)."""
    with _health_lock:
        return dict(_last_health)
