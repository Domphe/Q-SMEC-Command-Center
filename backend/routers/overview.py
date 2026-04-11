"""Overview router — KPIs, summaries, and dashboard aggregation."""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func

from backend.database import get_session
from backend.models.note import Note
from backend.models.email_cache import EmailCache
from backend.models.client import Client
from backend.models.pipeline import PipelineStatus
from backend.services.file_bridge import export_state

router = APIRouter()


@router.get("/overview")
def get_overview(session: Session = Depends(get_session)):
    # KPIs
    email_count = session.exec(select(func.count(EmailCache.id))).one()
    action_emails = session.exec(
        select(func.count(EmailCache.id)).where(EmailCache.action_required == True)  # noqa: E712
    ).one()
    client_count = session.exec(select(func.count(Client.id))).one()
    active_clients = session.exec(
        select(func.count(Client.id)).where(Client.status == "active")
    ).one()
    note_count = session.exec(select(func.count(Note.id))).one()
    pending_notes = session.exec(
        select(func.count(Note.id)).where(Note.status == "pending")
    ).one()
    uc_count = session.exec(select(func.count(PipelineStatus.uc))).one()

    # Pipeline phase breakdown
    phase_counts_raw = session.exec(
        select(PipelineStatus.phase, func.count(PipelineStatus.uc)).group_by(PipelineStatus.phase)
    ).all()
    phase_counts = {row[0]: row[1] for row in phase_counts_raw if row[0]}

    # Average progress
    avg_progress = session.exec(select(func.avg(PipelineStatus.progress))).one() or 0

    # Recent action emails
    action_stmt = (
        select(EmailCache)
        .where(EmailCache.action_required == True)  # noqa: E712
        .order_by(EmailCache.date.desc())
        .limit(5)
    )
    recent_action_emails = session.exec(action_stmt).all()

    # Recent notes
    recent_notes_stmt = select(Note).order_by(Note.created_at.desc()).limit(5)
    recent_notes = session.exec(recent_notes_stmt).all()

    kpis = {
        "emails": {"total": email_count, "action_required": action_emails},
        "clients": {"total": client_count, "active": active_clients},
        "notes": {"total": note_count, "pending": pending_notes},
        "pipeline": {"total_ucs": uc_count, "avg_progress": round(avg_progress, 1)},
        "repos": 18,
        "elements": 32,
    }

    # Export state to bridge for other Claude tools (P1-04)
    try:
        export_state(kpis, phase_counts)
    except Exception:
        pass  # non-critical — do not break overview endpoint

    return {
        "kpis": kpis,
        "phase_summary": phase_counts,
        "action_emails": recent_action_emails,
        "recent_notes": recent_notes,
    }
