"""Email sync service — shared logic between job and router.

Extracts the duplicated email fetch-triage-persist logic from
jobs/email_sync.py and routers/emails.py into a single function.
"""

import email.utils
import logging
from datetime import datetime, timezone

from sqlmodel import Session

from backend.models.email_cache import EmailCache
from backend.services.email_triage import categorize_email as triage_email
from backend.services.gmail_service import sync_recent_emails

logger = logging.getLogger(__name__)


def sync_and_persist_emails(session: Session, max_results: int = 50) -> dict:
    """Fetch recent emails from Gmail, triage, and persist new ones.

    Args:
        session: Active SQLModel session.
        max_results: Maximum emails to fetch from Gmail API.

    Returns:
        dict with keys: synced (int), new (int), emails (list of new EmailCache).
    """
    raw_emails = sync_recent_emails(max_results=max_results)

    new_count = 0
    new_emails = []
    for raw in raw_emails:
        existing = session.get(EmailCache, raw["id"])
        if existing:
            continue

        triage = triage_email(raw)

        # Parse the Gmail RFC 2822 date; fall back to current time only if absent
        parsed_date = None
        if raw.get("date"):
            try:
                parsed_date = email.utils.parsedate_to_datetime(raw["date"])
            except Exception:
                parsed_date = None
        if parsed_date is None:
            parsed_date = datetime.now(timezone.utc)

        cached = EmailCache(
            id=raw["id"],
            thread_id=raw.get("thread_id"),
            from_addr=raw.get("from_addr"),
            from_name=raw.get("from_name"),
            to_addr=raw.get("to_addr"),
            subject=raw.get("subject"),
            snippet=raw.get("snippet"),
            date=parsed_date,
            has_attachment=raw.get("has_attachment", False),
            is_unread=raw.get("is_unread", True),
            raw_labels=raw.get("raw_labels"),
            category=triage["category"],
            uc=triage["uc"],
            client=triage["client"],
            action_required=triage["action_required"],
            urgency=triage.get("urgency", "review"),
            confidence=triage.get("confidence", 0.5),
            categorized_by=triage["categorized_by"],
            synced_at=datetime.now(timezone.utc),
        )
        session.add(cached)
        new_emails.append(cached)
        new_count += 1

    session.commit()

    return {
        "synced": len(raw_emails),
        "new": new_count,
        "emails": new_emails,
    }
