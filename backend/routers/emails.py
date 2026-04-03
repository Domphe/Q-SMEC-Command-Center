"""Email triage router — Gmail cache with categorization."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from backend.database import get_session
from backend.models.email_cache import EmailCache

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
        pattern = "%{}%".format(search)
        statement = statement.where(
            EmailCache.subject.contains(search) | EmailCache.snippet.contains(search)  # type: ignore
        )
    emails = session.exec(statement).all()

    # Category counts
    counts_stmt = select(EmailCache.category, func.count(EmailCache.id)).group_by(EmailCache.category)
    counts_raw = session.exec(counts_stmt).all()
    counts = {row[0]: row[1] for row in counts_raw if row[0]}

    return {"emails": emails, "counts": counts, "total": len(emails)}


@router.post("/sync")
def sync_emails():
    """Trigger Gmail pull. Placeholder until Gmail OAuth is configured (Phase 4)."""
    return {"synced": 0, "new": 0, "message": "Gmail sync not configured yet — see Phase 4 in spec"}


@router.post("/{email_id}/categorize")
def categorize_email(
    email_id: str,
    category: Optional[str] = None,
    uc: Optional[str] = None,
    client: Optional[str] = None,
    action_required: Optional[bool] = None,
    session: Session = Depends(get_session),
):
    email = session.get(EmailCache, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    if category is not None:
        email.category = category
    if uc is not None:
        email.uc = uc
    if client is not None:
        email.client = client
    if action_required is not None:
        email.action_required = action_required
    email.categorized_by = "manual"
    session.add(email)
    session.commit()
    session.refresh(email)
    return email


@router.post("/{email_id}/create-note")
def create_note_from_email(email_id: str, session: Session = Depends(get_session)):
    """Create a note from email content, pre-tagged with UC/client."""
    from backend.models.note import Note
    from datetime import datetime

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
