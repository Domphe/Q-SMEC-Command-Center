"""Repos router — GitHub repo health status."""

import os
import subprocess
from typing import Optional

from fastapi import APIRouter

from backend.config import settings

router = APIRouter()

# Repo registry — matches the 18-repo ecosystem
REPO_REGISTRY = [
    {"name": "Orchestration-Engine", "domain": "ENGINE", "folder": "Q-SMEC-Orchestration-Engine",
     "desc": "Pipeline orchestration, PLAYBOOK.md v3.2.0"},
    {"name": "Orchestration-Docs", "domain": "DOCS", "folder": "Q-SMEC-Orchestration-Docs",
     "desc": "ECOSYSTEM_REGISTRY, ops tracker, reports"},
    {"name": "NIKET-Q-SMEC-Product", "domain": "PRODUCT", "folder": "NIKET-Q-SMEC-Product",
     "desc": "Product roadmap, milestone tracking"},
    {"name": "Quantum-Tools", "domain": "SCIENCE", "folder": "Q-SMEC-Quantum-Tools",
     "desc": "DFT runners, unified_pipeline.py, .venv"},
    {"name": "Quantum-Tools-Docs", "domain": "DOCS", "folder": "Q-SMEC-Quantum-Tools-Docs",
     "desc": "Physics parameter docs, DFT guides"},
    {"name": "Client-Databases", "domain": "DATA", "folder": "Q-SMEC-Client-Databases",
     "desc": "Client folders, UC data, NDA tracking"},
    {"name": "Client-Databases-Docs", "domain": "DOCS", "folder": "Q-SMEC-Client-Databases-Docs",
     "desc": "Client DB docs, white papers"},
    {"name": "Testing-Workflow-Seq", "domain": "TESTING", "folder": "Q-SMEC-Testing-Workflow-Sequence",
     "desc": "Test orchestration, workflow sequencing"},
    {"name": "Testing-Workflow-Docs", "domain": "DOCS", "folder": "Q-SMEC-Testing-Workflow-Docs",
     "desc": "Test docs, validation procedures"},
    {"name": "Niket-Work-Documents", "domain": "OFFICE", "folder": "Niket-Work-Documents",
     "desc": "Business docs, presentations, audits"},
    {"name": "Computer-Infra-Docs", "domain": "INFRA", "folder": "Computer-Infrastructure-Docs",
     "desc": "NIKET-HV-01 server docs, setup guides"},
    {"name": "Agentic-AI-Tools", "domain": "AI", "folder": "Q-SMEC-Agentic-AI-Tools",
     "desc": "Skills, agents, hooks, MCP configs"},
    {"name": "MCP-Server", "domain": "AI", "folder": "Q-SMEC-MCP-Server",
     "desc": "Custom MCP server, 10+ tools"},
    {"name": "Materials-Database", "domain": "SCIENCE", "folder": "Q-SMEC-Materials-Database",
     "desc": "32-element palette, material properties DB"},
    {"name": "EW-Sensor-Models", "domain": "SCIENCE", "folder": "Q-SMEC-EW-Sensor-Models",
     "desc": "EW sensor simulation models"},
    {"name": "ML-Potentials", "domain": "AI", "folder": "Q-SMEC-ML-Potentials",
     "desc": "ML interatomic potentials, MACE/NequIP"},
    {"name": "Benchmarks", "domain": "SCIENCE", "folder": "Q-SMEC-Benchmarks",
     "desc": "Performance benchmarks, validation suites"},
    {"name": "Publications", "domain": "DOCS", "folder": "Q-SMEC-Publications",
     "desc": "Papers, patent tracking, citations"},
]


def _get_repo_health(folder: str) -> dict:
    """Get basic git health for a local repo."""
    repo_path = os.path.join(settings.DATA1_PATH, folder)
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        return {"health": "missing", "branch": None, "last_commit": None, "dirty": False}

    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path, stderr=subprocess.DEVNULL, timeout=5,
        ).decode().strip()

        log_line = subprocess.check_output(
            ["git", "log", "-1", "--format=%H|%s|%ar"],
            cwd=repo_path, stderr=subprocess.DEVNULL, timeout=5,
        ).decode().strip()
        parts = log_line.split("|", 2)
        commit_hash = parts[0][:8] if parts else ""
        commit_msg = parts[1] if len(parts) > 1 else ""
        commit_age = parts[2] if len(parts) > 2 else ""

        status_out = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=repo_path, stderr=subprocess.DEVNULL, timeout=5,
        ).decode().strip()
        dirty = bool(status_out)

        # Health rating
        health = "good"
        if dirty:
            health = "fair"
        if "week" in commit_age or "month" in commit_age:
            health = "caution" if health == "good" else "fair"

        return {
            "health": health,
            "branch": branch,
            "last_commit": commit_msg,
            "commit_hash": commit_hash,
            "commit_age": commit_age,
            "dirty": dirty,
        }
    except (subprocess.SubprocessError, OSError):
        return {"health": "error", "branch": None, "last_commit": None, "dirty": False}


@router.get("")
def list_repos():
    repos = []
    for repo in REPO_REGISTRY:
        health = _get_repo_health(repo["folder"])
        repos.append({
            "name": repo["name"],
            "domain": repo["domain"],
            "desc": repo["desc"],
            "folder": repo["folder"],
            **health,
        })
    return {"repos": repos, "total": len(repos)}


@router.get("/{name}/health")
def get_repo_health(name: str):
    match = None
    for repo in REPO_REGISTRY:
        if repo["name"].lower() == name.lower() or repo["folder"].lower() == name.lower():
            match = repo
            break
    if not match:
        return {"error": "Repo not found: {}".format(name)}
    health = _get_repo_health(match["folder"])
    return {"name": match["name"], "folder": match["folder"], **health}
