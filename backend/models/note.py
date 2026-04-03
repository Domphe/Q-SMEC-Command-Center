"""Note model — notes with tags, status, and AI tool handoff."""

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class NoteBase(SQLModel):
    text: str
    tag: str = "general"  # general|action|research|client|pipeline|idea
    status: str = "note"  # note|pending|in_progress|done
    target_tool: Optional[str] = None  # code|cowork|project|null
    target_model: Optional[str] = None  # opus|sonnet|gemini|null
    context: Optional[dict] = Field(default=None, sa_column=Column(JSON))


class Note(NoteBase, table=True):
    __tablename__ = "notes"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NoteCreate(NoteBase):
    pass


class NoteUpdate(SQLModel):
    text: Optional[str] = None
    tag: Optional[str] = None
    status: Optional[str] = None
    target_tool: Optional[str] = None
    target_model: Optional[str] = None
    context: Optional[dict] = None
