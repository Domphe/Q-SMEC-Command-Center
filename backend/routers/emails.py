"""Email triage router — Gmail cache with categorization."""

import logging
from datetime import datetime
import email.utils
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from backend.database import get_session
from backend.models.email_cache import EmailCache
from backend.services.gmail_service import is_gmail_configured, sync_recent_emails
from backend.services.email_triage import (
    categorize_email as triage_email,
    maybe_learn_sender_rule,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
def list_emails(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    session: Session = Depends(get_session),
):
    statement = select(EmailCache).order_by(EmailCache.date.desc()).limit(limit)
    if category:
        statement = statement.where(EmailCache.category == category)
    if search:
        statement = statement.where(
            EmailCache.subject.contains(search) | EmailCache.snippet.contains(search)  # type: ignore
        )
    emails = session.exec(statement).all()

    # Category counts
    counts_stmt = select(EmailCache.category, func.count(EmailCache.id)).group_by(EmailCache.category)
    counts_raw = session.exec(counts_stmt).all()
    counts = {row[0]: row[1] for row in counts_raw if row[0]}

    return {"emails": emails, "counts": counts, "total": len(emails)}


@router.get("/learning-stats")
def learning_stats(
    session: Session = Depends(get_session),
):
    """Return feedback and learning metrics."""
    from backend.models.email_feedback import (
        EmailFeedback, LearnedSenderRule,
    )
    from datetime import timedelta

    cutoff = datetime.utcnow() - timedelta(days=7)

    total_fb = session.exec(
        select(func.count(EmailFeedback.id))
    ).one()

    learned = session.exec(
        select(func.count(LearnedSenderRule.sender))
    ).one()

    ai_recent = session.exec(
        select(func.count(EmailCache.id)).where(
            EmailCache.categorized_by == "ai",
            EmailCache.synced_at >= cutoff,
        )
    ).one()

    manual_recent = session.exec(
        select(func.count(EmailFeedback.id)).where(
            EmailFeedback.corrected_by == "manual",
            EmailFeedback.created_at >= cutoff,
        )
    ).one()

    return {
        "total_feedback": total_fb,
        "learned_rules": learned,
        "ai_categorized_last_7_days": ai_recent,
        "manual_corrections_last_7_days": manual_recent,
    }


@router.post("/sync")
def sync_emails_endpoint(limit: int = 500, session: Session = Depends(get_session)):
    """Trigger Gmail pull — fetches recent emails and categorizes them."""
    if not is_gmail_configured():
        return {
            "synced": 0, "new": 0,
            "message": "Gmail not configured. Place client_secret.json in the repo root and run the OAuth flow.",
        }

    try:
        raw_emails = sync_recent_emails(max_results=limit)
    except Exception as e:
        logger.error("Gmail sync failed: %s", e)
        return {"synced": 0, "new": 0, "error": str(e)}

    new_count = 0
    for raw in raw_emails:
        existing = session.get(EmailCache, raw["id"])
        if existing:
            continue

        # Triage
        triage = triage_email(raw)

        email = EmailCache(
            id=raw["id"],
            thread_id=raw.get("thread_id"),
            from_addr=raw.get("from_addr"),
            from_name=raw.get("from_name"),
            to_addr=raw.get("to_addr"),
            subject=raw.get("subject"),
            snippet=raw.get("snippet"),
            date=email.utils.parsedate_to_datetime(raw.get("date", "")) if raw.get("date") else datetime.utcnow(),
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
            synced_at=datetime.utcnow(),
        )
        session.add(email)
        new_count += 1

    session.commit()
    return {"synced": len(raw_emails), "new": new_count}


@router.post("/{email_id}/categorize")
def categorize_email_endpoint(
    email_id: str,
    category: Optional[str] = None,
    uc: Optional[str] = None,
    client: Optional[str] = None,
    action_required: Optional[bool] = None,
    urgency: Optional[str] = None,
    session: Session = Depends(get_session),
):
    from backend.models.email_feedback import EmailFeedback

    email = session.get(EmailCache, email_id)
    if not email:
        raise HTTPException(
            status_code=404, detail="Email not found",
        )

    original_cat = email.category
    original_urg = email.urgency

    if category is not None:
        email.category = category
    if uc is not None:
        email.uc = uc
    if client is not None:
        email.client = client
    if action_required is not None:
        email.action_required = action_required
    if urgency is not None:
        email.urgency = urgency
    email.categorized_by = "manual"

    # Log feedback for learning
    if category and category != original_cat:
        feedback = EmailFeedback(
            email_id=email_id,
            original_category=original_cat,
            corrected_category=category,
            original_urgency=original_urg,
            corrected_urgency=urgency,
            corrected_by="manual",
        )
        session.add(feedback)

    session.add(email)
    session.commit()
    session.refresh(email)

    # Trigger learning check
    if category and category != original_cat:
        maybe_learn_sender_rule(
            email.from_addr, session,
        )

    return email


@router.patch("/{email_id}")
def patch_email(
    email_id: str,
    action_required: Optional[bool] = None,
    is_unread: Optional[bool] = None,
    urgency: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """Partial update — toggle flags or urgency."""
    email = session.get(EmailCache, email_id)
    if not email:
        raise HTTPException(
            status_code=404, detail="Email not found",
        )
    if action_required is not None:
        email.action_required = action_required
    if is_unread is not None:
        email.is_unread = is_unread
    if urgency is not None:
        email.urgency = urgency
    session.add(email)
    session.commit()
    session.refresh(email)
    return email


@router.post("/{email_id}/create-note")
def create_note_from_email(email_id: str, session: Session = Depends(get_session)):
    """Create a note from email content, pre-tagged with UC/client."""
    from backend.models.note import Note

    email = session.get(EmailCache, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    context = {}
    if email.uc:
        context["uc"] = email.uc
    if email.client:
        context["client"] = email.client

    note = Note(
        text="[Email] {subject}\n{snippet}".format(subject=email.subject, snippet=email.snippet or ""),
        tag="action" if email.action_required else "research",
        status="pending" if email.action_required else "note",
        context=context if context else None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(note)
    session.commit()
    session.refresh(note)
    return {"created": True, "note": note}
