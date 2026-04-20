"""Email cache model — cached Gmail metadata with triage fields."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON
from sqlmodel import Column, Field, SQLModel


class EmailCacheBase(SQLModel):
    thread_id: Optional[str] = None
    from_addr: Optional[str] = None
    from_name: Optional[str] = None
    to_addr: Optional[str] = None
    subject: Optional[str] = None
    snippet: Optional[str] = None
    date: Optional[datetime] = None
    category: Optional[str] = None  # research|client|opportunity|business|noise
    uc: Optional[str] = None
    client: Optional[str] = None
    has_attachment: bool = False
    is_unread: bool = True
    action_required: bool = False
    urgency: Optional[str] = "review"  # respond|review|archive
    confidence: float = 0.5
    raw_labels: Optional[list] = Field(
        default=None,
        sa_column=Column(JSON),
    )
    categorized_by: Optional[str] = None  # rule|ai|manual


class EmailCache(EmailCacheBase, table=True):
    __tablename__ = "email_cache"

    id: str = Field(primary_key=True)  # Gmail message ID
    synced_at: datetime = Field(default_factory=datetime.utcnow)


class EmailCacheCreate(EmailCacheBase):
    id: str
