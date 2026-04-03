"""Gmail API wrapper — OAuth2 authentication and email operations."""

import os
import base64
from datetime import datetime
from typing import Optional

from backend.config import settings

# Lazy imports — these are heavy and only needed when Gmail is configured
_service = None


def _get_credentials():
    """Get or refresh Gmail OAuth2 credentials."""
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    creds = None

    token_path = settings.GMAIL_TOKEN_PATH
    secret_path = settings.GMAIL_CLIENT_SECRET_PATH

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(secret_path):
                raise FileNotFoundError(
                    "Gmail client_secret.json not found at {}. "
                    "Download from Google Cloud Console.".format(secret_path)
                )
            flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


def get_gmail_service():
    """Get authenticated Gmail API service (singleton)."""
    global _service
    if _service is None:
        from googleapiclient.discovery import build
        creds = _get_credentials()
        _service = build("gmail", "v1", credentials=creds)
    return _service


def is_gmail_configured() -> bool:
    """Check if Gmail OAuth credentials are available."""
    return (
        os.path.exists(settings.GMAIL_TOKEN_PATH)
        or os.path.exists(settings.GMAIL_CLIENT_SECRET_PATH)
    )


def list_messages(query: str = "", max_results: int = 50) -> list:
    """List Gmail messages matching a query."""
    if not is_gmail_configured():
        return []

    service = get_gmail_service()
    results = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    return messages


def get_message(msg_id: str) -> dict:
    """Get full message details by ID."""
    service = get_gmail_service()
    msg = service.users().messages().get(
        userId="me", id=msg_id, format="metadata",
        metadataHeaders=["From", "To", "Subject", "Date"],
    ).execute()

    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

    # Parse from field
    from_raw = headers.get("From", "")
    from_name = from_raw.split("<")[0].strip().strip('"') if "<" in from_raw else from_raw
    from_addr = from_raw.split("<")[1].rstrip(">") if "<" in from_raw else from_raw

    # Check for attachments
    parts = msg.get("payload", {}).get("parts", [])
    has_attachment = any(
        p.get("filename") and p["filename"] != ""
        for p in parts
    ) if parts else False

    return {
        "id": msg["id"],
        "thread_id": msg.get("threadId"),
        "from_addr": from_addr,
        "from_name": from_name,
        "to_addr": headers.get("To", ""),
        "subject": headers.get("Subject", ""),
        "snippet": msg.get("snippet", ""),
        "date": headers.get("Date", ""),
        "has_attachment": has_attachment,
        "is_unread": "UNREAD" in msg.get("labelIds", []),
        "raw_labels": msg.get("labelIds", []),
    }


def sync_recent_emails(max_results: int = 50) -> list:
    """Fetch recent emails and return parsed list."""
    if not is_gmail_configured():
        return []

    messages = list_messages(query="in:inbox", max_results=max_results)
    parsed = []
    for msg_ref in messages:
        try:
            parsed.append(get_message(msg_ref["id"]))
        except Exception:
            continue
    return parsed
