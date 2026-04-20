"""Email feedback + learned sender rules models."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class EmailFeedback(SQLModel, table=True):
    __tablename__ = "email_feedback"

    id: Optional[int] = Field(default=None, primary_key=True)
    email_id: str
    original_category: Optional[str] = None
    corrected_category: str
    original_urgency: Optional[str] = None
    corrected_urgency: Optional[str] = None
    corrected_by: str = "manual"  # manual | ai
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
    )


class LearnedSenderRule(SQLModel, table=True):
    __tablename__ = "learned_sender_rules"

    sender: str = Field(primary_key=True)
    category: str
    confidence: float = 0.8
    sample_count: int = 0
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
    )
