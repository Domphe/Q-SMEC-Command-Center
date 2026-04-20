"""File bridge — read/write JSON bridge files for AI tool integration."""

import json
import os
from datetime import datetime

from backend.config import settings


def _bridge_path(filename: str) -> str:
    """Get full path for a bridge file."""
    return os.path.join(settings.BRIDGE_PATH, filename)


def export_state(kpis: dict, pipeline_summary: dict) -> str:
    """Export current command center state to bridge."""
    path = _bridge_path("command_center_state.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    payload = {
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "kpis": kpis,
        "pipeline_summary": pipeline_summary,
    }

    with open(path, "w") as f:
        json.dump(payload, f, indent=2)

    return path


def export_email_digest(emails: list) -> str:
    """Export email triage results to bridge."""
    path = _bridge_path("email_digest.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    payload = {
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "emails": emails,
        "total": len(emails),
    }

    with open(path, "w") as f:
        json.dump(payload, f, indent=2)

    return path


def read_bridge_file(filename: str) -> dict:
    """Read a bridge file. Returns empty dict if not found."""
    path = _bridge_path(filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)
