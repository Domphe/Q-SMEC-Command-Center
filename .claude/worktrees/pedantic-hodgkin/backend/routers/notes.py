"""Notes CRUD router with AI bridge export."""

import json
import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models.note import Note, NoteCreate, NoteUpdate
from backend.config import settings

router = APIRouter()


@router.get("")
def list_notes(
    tag: Optional[str] = None,
    status: Optional[str] = None,
    session: Session = Depends(get_session),
):
    statement = select(Note).order_by(Note.created_at.desc())
    if tag:
        statement = statement.where(Note.tag == tag)
    if status:
        statement = statement.where(Note.status == status)
    notes = session.exec(statement).all()
    return {"notes": notes, "count": len(notes)}


@router.post("", status_code=201)
def create_note(note_in: NoteCreate, session: Session = Depends(get_session)):
    note = Note.model_validate(note_in)
    note.created_at = datetime.utcnow()
    note.updated_at = datetime.utcnow()
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.put("/{note_id}")
def update_note(note_id: int, note_in: NoteUpdate, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    update_data = note_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(note, key, value)
    note.updated_at = datetime.utcnow()
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.delete("/{note_id}")
def delete_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(note)
    session.commit()
    return {"deleted": True, "id": note_id}


@router.post("/{note_id}/route")
def route_note(note_id: int, session: Session = Depends(get_session)):
    """Route a note to an AI tool by exporting it to the bridge."""
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.status = "pending"
    note.updated_at = datetime.utcnow()
    session.add(note)
    session.commit()
    session.refresh(note)
    _export_pending_notes(session)
    return {"routed": True, "note": note}


@router.post("/export")
def export_notes(session: Session = Depends(get_session)):
    """Export all pending notes to bridge JSON."""
    count = _export_pending_notes(session)
    return {"exported": count}


def _export_pending_notes(session: Session) -> int:
    """Write pending notes to bridge/pending_notes.json."""
    statement = select(Note).where(Note.status == "pending")
    pending = session.exec(statement).all()

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

    return len(pending)
