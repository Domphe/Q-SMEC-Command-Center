"""Client model — client/partner records with UC associations."""

from datetime import date, datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class ClientBase(SQLModel):
    name: str = Field(unique=True)
    status: str = "prospect"  # active|prospect|early|inactive
    type: str = "client"  # client|partner|research
    priority: str = "medium"  # high|medium|low
    contact: Optional[str] = None
    sector: Optional[str] = None
    uc: Optional[list] = Field(default=None, sa_column=Column(JSON))
    nda_status: Optional[str] = None
    data_size: Optional[str] = None
    notes: Optional[str] = None
    last_touch: Optional[date] = None


class Client(ClientBase, table=True):
    __tablename__ = "clients"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(SQLModel):
    name: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[str] = None
    contact: Optional[str] = None
    sector: Optional[str] = None
    uc: Optional[list] = None
    nda_status: Optional[str] = None
    data_size: Optional[str] = None
    notes: Optional[str] = None
    last_touch: Optional[date] = None
