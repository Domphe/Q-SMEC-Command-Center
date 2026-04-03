"""Background job: export pending notes to bridge every 5 minutes."""

import json
import logging
import os
from datetime import datetime

from sqlmodel import Session, select

from backend.database import engine
from backend.models.note import Note
from backend.config import settings

logger = logging.getLogger(__name__)


def run_note_export():
    """Export pending notes to bridge/pending_notes.json."""
    with Session(engine) as session:
        statement = select(Note).where(Note.status == "pending")
        pending = session.exec(statement).all()

        if not pending:
            logger.debug("No pending notes to export")
            return

        bridge_path = os.path.join(settings.BRIDGE_PATH, "pending_notes.json")
        os.makedirs(os.path.dirname(bridge_path), exist_ok=True)

        payload = {
            "exported_at": datetime.utcnow().isoformat() + "Z",
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

        with open(bridge_path, "w") as f:
            json.dump(payload, f, indent=2)

        logger.info("Exported %d pending notes to bridge", len(pending))
