"""Application configuration loaded from environment variables."""

import os

from dotenv import load_dotenv

# Project root is one level up from backend/
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))


class Settings:
    """Application settings from .env file."""

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", os.path.join(_PROJECT_ROOT, "command_center.db"))
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "")

    # Gmail
    GMAIL_CLIENT_SECRET_PATH: str = os.getenv(
        "GMAIL_CLIENT_SECRET_PATH", os.path.join(_PROJECT_ROOT, "client_secret.json")
    )
    GMAIL_TOKEN_PATH: str = os.getenv("GMAIL_TOKEN_PATH", os.path.join(_PROJECT_ROOT, "token.json"))
    GMAIL_USER: str = os.getenv("GMAIL_USER", "s.dely@niketllc.com")

    # GitHub
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_ORG: str = os.getenv("GITHUB_ORG", "Domphe")

    # Anthropic
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Google Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # File Bridge
    BRIDGE_PATH: str = os.getenv("BRIDGE_PATH", os.path.join(_PROJECT_ROOT, "bridge"))

    # Ecosystem
    DATA1_PATH: str = os.getenv("DATA1_PATH", "/mnt/e/Data1")
    PLAYBOOK_PATH: str = os.getenv("PLAYBOOK_PATH", "")
    SYNC_PATH: str = os.getenv("SYNC_PATH", "")


settings = Settings()
