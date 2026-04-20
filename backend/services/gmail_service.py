"""Gmail API wrapper — supports both OAuth2 (desktop) and Service Account auth."""

import json
import logging
import os
from typing import Optional

from backend.config import settings

logger = logging.getLogger(__name__)

# Full Gmail access — read, send, modify, labels, settings
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.settings.basic",
    "https://mail.google.com/",  # full mailbox access
]

# Lazy imports — these are heavy and only needed when Gmail is configured
_service = None


def _detect_credential_type(path: str) -> Optional[str]:
    """Detect if a JSON credential file is a service account or OAuth2 client."""
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        data = json.load(f)
    if data.get("type") == "service_account":
        return "service_account"
    if data.get("installed") or data.get("web"):
        return "oauth2"
    return None


def _get_service_account_credentials():
    """Build credentials from a service account key with domain-wide delegation."""
    from google.oauth2 import service_account

    SCOPES = GMAIL_SCOPES
    sa_path = settings.GMAIL_CLIENT_SECRET_PATH

    creds = service_account.Credentials.from_service_account_file(sa_path, scopes=SCOPES)

    # Delegate to the target user's mailbox
    delegated_user = settings.GMAIL_USER
    if delegated_user:
        creds = creds.with_subject(delegated_user)

    return creds


def _get_oauth2_credentials():
    """Get or refresh OAuth2 credentials (desktop app flow)."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    SCOPES = GMAIL_SCOPES
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
                    "Gmail client_secret.json not found at {}. Download from Google Cloud Console.".format(secret_path)
                )
            flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


def _get_credentials():
    """Auto-detect credential type and return appropriate credentials."""
    secret_path = settings.GMAIL_CLIENT_SECRET_PATH
    cred_type = _detect_credential_type(secret_path)

    if cred_type == "service_account":
        return _get_service_account_credentials()
    elif cred_type == "oauth2":
        return _get_oauth2_credentials()
    elif os.path.exists(settings.GMAIL_TOKEN_PATH):
        # Existing token from previous OAuth2 flow
        return _get_oauth2_credentials()
    else:
        raise FileNotFoundError(
            "No Gmail credentials found. Place either a service account key or OAuth2 client_secret.json at {}".format(
                secret_path
            )
        )


def get_gmail_service():
    """Get authenticated Gmail API service (singleton)."""
    global _service
    if _service is None:
        from googleapiclient.discovery import build

        creds = _get_credentials()
        _service = build("gmail", "v1", credentials=creds)
    return _service


def is_gmail_configured() -> bool:
    """Check if any Gmail credentials are available."""
    return os.path.exists(settings.GMAIL_TOKEN_PATH) or os.path.exists(settings.GMAIL_CLIENT_SECRET_PATH)


def get_auth_type() -> Optional[str]:
    """Return which auth method is configured."""
    return _detect_credential_type(settings.GMAIL_CLIENT_SECRET_PATH)


def list_messages(query: str = "", max_results: int = 500) -> list:
    """List Gmail messages matching a query. Paginates for >500 results."""
    if not is_gmail_configured():
        return []

    service = get_gmail_service()
    user_id = settings.GMAIL_USER or "me"
    messages = []
    page_token = None
    page_size = min(max_results, 500)

    while len(messages) < max_results:
        request_args = {"userId": user_id, "q": query, "maxResults": page_size}
        if page_token:
            request_args["pageToken"] = page_token

        results = service.users().messages().list(**request_args).execute()
        messages.extend(results.get("messages", []))
        page_token = results.get("nextPageToken")

        if not page_token:
            break

    return messages[:max_results]


def get_message(msg_id: str) -> dict:
    """Get full message details by ID."""
    service = get_gmail_service()
    user_id = settings.GMAIL_USER or "me"
    msg = (
        service.users()
        .messages()
        .get(
            userId=user_id,
            id=msg_id,
            format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"],
        )
        .execute()
    )

    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

    # Parse from field using stdlib for robustness
    from_raw = headers.get("From", "")
    try:
        import email.utils as _email_utils

        _parsed_name, _parsed_addr = _email_utils.parseaddr(from_raw)
        from_name = _parsed_name or _parsed_addr
        from_addr = _parsed_addr or from_raw
    except Exception:
        from_name = from_raw
        from_addr = from_raw

    # Check for attachments
    parts = msg.get("payload", {}).get("parts", [])
    has_attachment = any(p.get("filename") and p["filename"] != "" for p in parts) if parts else False

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


def sync_recent_emails(max_results: int = 500) -> list:
    """Fetch recent emails and return parsed list."""
    if not is_gmail_configured():
        return []

    messages = list_messages(query="in:inbox", max_results=max_results)
    parsed = []
    for msg_ref in messages:
        try:
            parsed.append(get_message(msg_ref["id"]))
        except Exception as e:
            logger.warning("Failed to parse message %s: %s", msg_ref.get("id"), e)
            continue
    return parsed
