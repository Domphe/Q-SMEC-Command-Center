"""Clients CRUD router."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models.client import Client, ClientCreate, ClientUpdate

router = APIRouter()


@router.get("")
def list_clients(
    type: Optional[str] = None,
    status: Optional[str] = None,
    session: Session = Depends(get_session),
):
    statement = select(Client).order_by(Client.priority.desc(), Client.last_touch.desc())
    if type:
        statement = statement.where(Client.type == type)
    if status:
        statement = statement.where(Client.status == status)
    clients = session.exec(statement).all()
    return {"clients": clients, "count": len(clients)}


@router.post("", status_code=201)
def create_client(client_in: ClientCreate, session: Session = Depends(get_session)):
    client = Client.model_validate(client_in)
    client.created_at = datetime.utcnow()
    client.updated_at = datetime.utcnow()
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@router.get("/{client_id}")
def get_client(client_id: int, session: Session = Depends(get_session)):
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/{client_id}")
def update_client(client_id: int, client_in: ClientUpdate, session: Session = Depends(get_session)):
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    update_data = client_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(client, key, value)
    client.updated_at = datetime.utcnow()
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@router.get("/{client_id}/emails")
def get_client_emails(client_id: int, session: Session = Depends(get_session)):
    """Get all emails mentioning this client."""
    from backend.models.email_cache import EmailCache

    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    statement = select(EmailCache).where(EmailCache.client == client.name).order_by(EmailCache.date.desc())
    emails = session.exec(statement).all()
    return {"client": client.name, "emails": emails, "count": len(emails)}
