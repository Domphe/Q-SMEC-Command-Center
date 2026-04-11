"""Notes CRUD router with AI bridge export."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models.note import Note, NoteCreate, NoteUpdate
from backend.services.note_export_service import export_pending_notes

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
    note.created_at = datetime.now(timezone.utc)
    note.updated_at = datetime.now(timezone.utc)
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
    note.updated_at = datetime.now(timezone.utc)
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
    note.updated_at = datetime.now(timezone.utc)
    session.add(note)
    session.commit()
    session.refresh(note)
    export_pending_notes(session)
    return {"routed": True, "note": note}


@router.post("/export")
def export_notes(session: Session = Depends(get_session)):
    """Export all pending notes to bridge JSON."""
    count = export_pending_notes(session)
    return {"exported": count}
