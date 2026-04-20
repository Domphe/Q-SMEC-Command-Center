"""Pipeline status router — UC pipeline tracking."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models.pipeline import PipelineStatus

router = APIRouter()

UC_CATEGORIES = [
    {
        "cat": "Optical Warfare / DE / C-UAS",
        "color": "#ef4444",
        "ucs": ["UC01", "UC02", "UC03", "UC04", "UC09", "UC18", "UC19", "UC20"],
    },
    {
        "cat": "Electronic Warfare / C / NKE",
        "color": "#f59e0b",
        "ucs": ["UC05", "UC06", "UC08", "UC10", "UC11", "UC12", "UC13", "UC16", "UC23"],
    },
    {"cat": "Deep Underground / Infrastructure", "color": "#06b6d4", "ucs": ["UC07", "UC21", "UC22"]},
    {"cat": "PNT", "color": "#8b5cf6", "ucs": ["UC14", "UC15"]},
    {"cat": "Counter-UAS", "color": "#10b981", "ucs": ["UC04", "UC08", "UC17"]},
]


@router.get("")
def list_pipeline(
    phase: Optional[str] = None,
    session: Session = Depends(get_session),
):
    statement = select(PipelineStatus).order_by(PipelineStatus.uc)
    if phase:
        statement = statement.where(PipelineStatus.phase == phase)
    items = session.exec(statement).all()

    # Build phase summary
    phases = {}
    for item in items:
        p = item.phase or "Unknown"
        if p not in phases:
            phases[p] = 0
        phases[p] += 1

    active = [i for i in items if i.progress > 0]
    return {
        "pipeline": items,
        "active": active,
        "categories": UC_CATEGORIES,
        "phases": phases,
        "total": len(items),
    }


@router.get("/{uc}")
def get_uc_status(uc: str, session: Session = Depends(get_session)):
    uc_upper = uc.upper()
    status = session.get(PipelineStatus, uc_upper)
    if not status:
        raise HTTPException(status_code=404, detail="UC not found: {}".format(uc_upper))

    # Find which categories this UC belongs to
    categories = [c["cat"] for c in UC_CATEGORIES if uc_upper in c["ucs"]]
    return {"uc": status, "categories": categories}
