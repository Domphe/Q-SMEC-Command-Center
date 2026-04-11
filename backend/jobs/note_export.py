"""Background job: export pending notes to bridge every 5 minutes."""

import logging

from sqlmodel import Session

from backend.database import engine
from backend.services.note_export_service import export_pending_notes

logger = logging.getLogger(__name__)


def run_note_export():
    """Export pending notes to bridge/pending_notes.json."""
    with Session(engine) as session:
        count = export_pending_notes(session)

    if count:
        logger.info("Exported %d pending notes to bridge", count)
    else:
        logger.debug("No pending notes to export")
