"""Note export service — shared logic between job and router.

Extracts the duplicated pending-notes-to-bridge export from
jobs/note_export.py and routers/notes.py into a single function.
"""

import json
import logging
import os
from datetime import datetime, timezone

from sqlmodel import Session, select

from backend.models.note import Note
from backend.config import settings

logger = logging.getLogger(__name__)


def export_pending_notes(session: Session) -> int:
    """Write pending notes to bridge/pending_notes.json.

    Args:
        session: Active SQLModel session.

    Returns:
        Number of pending notes exported.
    """
    statement = select(Note).where(Note.status == "pending")
    pending = session.exec(statement).all()

    bridge_path = os.path.join(settings.BRIDGE_PATH, "pending_notes.json")
    os.makedirs(os.path.dirname(bridge_path), exist_ok=True)

    payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "notes": [
            {
                "id": n.id,
                "text": n.text,
                "tag": n.tag,
                "status": n.status,
                "target_tool": n.target_tool,
                "target_model": n.target_model,
                "created": n.created_at.isoformat() if n.created_at else None,
                "context": n.context,
            }
            for n in pending
        ],
    }

    try:
        with open(bridge_path, "w") as f:
            json.dump(payload, f, indent=2)
    except IOError as e:
        logger.error("Failed to write bridge file %s: %s", bridge_path, e)
        return 0

    return len(pending)
