"""Email triage router — Gmail cache with categorization."""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, func, select

from backend.database import get_session
from backend.models.email_cache import EmailCache
from backend.services.email_sync_service import sync_and_persist_emails
from backend.services.email_triage import (
    maybe_learn_sender_rule,
)
from backend.services.gmail_service import is_gmail_configured

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
    from datetime import timedelta

    from backend.models.email_feedback import (
        EmailFeedback,
        LearnedSenderRule,
    )

    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    total_fb = session.exec(select(func.count(EmailFeedback.id))).one()

    learned = session.exec(select(func.count(LearnedSenderRule.sender))).one()

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
            "synced": 0,
            "new": 0,
            "message": "Gmail not configured. Place client_secret.json in the repo root and run the OAuth flow.",
        }

    try:
        result = sync_and_persist_emails(session, max_results=limit)
    except Exception as e:
        logger.error("Gmail sync failed: %s", e)
        return {"synced": 0, "new": 0, "error": "sync failed"}

    return {"synced": result["synced"], "new": result["new"]}


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
            status_code=404,
            detail="Email not found",
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
            email.from_addr,
            session,
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
            status_code=404,
            detail="Email not found",
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
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    session.add(note)
    session.commit()
    session.refresh(note)
    return {"created": True, "note": note}
