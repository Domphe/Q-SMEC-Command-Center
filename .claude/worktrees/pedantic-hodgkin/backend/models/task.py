"""AI task model — tracks AI-routed tasks and their results."""

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class AITaskBase(SQLModel):
    description: str
    complexity_score: Optional[int] = None
    recommended_model: Optional[str] = None
    actual_model: Optional[str] = None
    tool: Optional[str] = None  # code|cowork|project
    status: str = "pending"  # pending|executing|completed|failed
    result: Optional[str] = None
    tokens_used: Optional[int] = None
    duration_ms: Optional[int] = None


class AITask(AITaskBase, table=True):
    __tablename__ = "ai_tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class AITaskCreate(SQLModel):
    description: str
    tool: Optional[str] = None
