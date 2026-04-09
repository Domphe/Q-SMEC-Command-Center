"""Agent digest router — serves bridge/agent_digest.json."""

import json
import os

from fastapi import APIRouter

router = APIRouter()

BRIDGE_PATH = os.getenv(
    "BRIDGE_PATH", "./bridge"
)


@router.get("/digest")
def get_digest():
    """Return latest agent digest from bridge."""
    path = os.path.join(
        BRIDGE_PATH, "agent_digest.json",
    )
    if not os.path.exists(path):
        return {
            "generated_at": None,
            "summaries": [],
            "action_items": [],
        }
    with open(path) as f:
        return json.load(f)
