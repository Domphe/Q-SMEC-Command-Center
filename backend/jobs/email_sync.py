"""Background job: sync Gmail every 15 minutes."""

import logging
from datetime import datetime

from sqlmodel import Session, select

from backend.database import engine
from backend.models.email_cache import EmailCache
from backend.services.gmail_service import is_gmail_configured, sync_recent_emails
from backend.services.email_triage import categorize_email as triage_email
from backend.services.file_bridge import export_email_digest

logger = logging.getLogger(__name__)


def run_email_sync():
    """Pull recent emails from Gmail, triage, and cache."""
    if not is_gmail_configured():
        logger.debug("Gmail not configured — skipping email sync")
        return

    logger.info("Starting email sync job...")
    try:
        raw_emails = sync_recent_emails(max_results=50)
    except Exception as e:
        logger.error("Gmail sync failed: %s", e)
        return

    new_count = 0
    with Session(engine) as session:
        for raw in raw_emails:
            existing = session.get(EmailCache, raw["id"])
            if existing:
                continue

            triage = triage_email(raw)
            email = EmailCache(
                id=raw["id"],
                thread_id=raw.get("thread_id"),
                from_addr=raw.get("from_addr"),
                from_name=raw.get("from_name"),
                to_addr=raw.get("to_addr"),
                subject=raw.get("subject"),
                snippet=raw.get("snippet"),
                date=datetime.utcnow(),
                has_attachment=raw.get("has_attachment", False),
                is_unread=raw.get("is_unread", True),
                raw_labels=raw.get("raw_labels"),
                category=triage["category"],
                uc=triage["uc"],
                client=triage["client"],
                action_required=triage["action_required"],
                categorized_by=triage["categorized_by"],
                synced_at=datetime.utcnow(),
            )
            session.add(email)
            new_count += 1

        session.commit()

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
                "id": e.id, "subject": e.subject, "from": e.from_name,
                "category": e.category, "uc": e.uc, "client": e.client,
            }
            for e in action_emails
        ]
        export_email_digest(digest)

    logger.info("Email sync complete: %d fetched, %d new", len(raw_emails), new_count)
