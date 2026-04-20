"""Background job: sync Gmail every 15 minutes."""

import logging

from sqlmodel import Session, select

from backend.database import engine
from backend.models.email_cache import EmailCache
from backend.services.email_sync_service import sync_and_persist_emails
from backend.services.file_bridge import export_email_digest
from backend.services.gmail_service import is_gmail_configured

logger = logging.getLogger(__name__)


def run_email_sync():
    """Pull recent emails from Gmail, triage, and cache."""
    if not is_gmail_configured():
        logger.debug("Gmail not configured — skipping email sync")
        return

    logger.info("Starting email sync job...")
    try:
        with Session(engine) as session:
            result = sync_and_persist_emails(session, max_results=50)

            # Export action emails to bridge
            action_stmt = (
                select(EmailCache)
                .where(EmailCache.action_required == True)  # noqa: E712
                .order_by(EmailCache.date.desc())
                .limit(20)
            )
            action_emails = session.exec(action_stmt).all()
            digest = [
                {
                    "id": e.id,
                    "subject": e.subject,
                    "from": e.from_name,
                    "category": e.category,
                    "uc": e.uc,
                    "client": e.client,
                }
                for e in action_emails
            ]
            export_email_digest(digest)

        logger.info(
            "Email sync complete: %d fetched, %d new",
            result["synced"],
            result["new"],
        )
    except Exception as e:
        logger.error("Gmail sync failed: %s", e)
