"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings from .env file."""

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "./command_center.db")
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "")

    # Gmail
    GMAIL_CLIENT_SECRET_PATH: str = os.getenv("GMAIL_CLIENT_SECRET_PATH", "./client_secret.json")
    GMAIL_TOKEN_PATH: str = os.getenv("GMAIL_TOKEN_PATH", "./token.json")
    GMAIL_USER: str = os.getenv("GMAIL_USER", "")

    # GitHub
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_ORG: str = os.getenv("GITHUB_ORG", "Domphe")

    # Anthropic
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Google Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # File Bridge
    BRIDGE_PATH: str = os.getenv("BRIDGE_PATH", "./bridge")

    # Ecosystem
    DATA1_PATH: str = os.getenv("DATA1_PATH", "/mnt/e/Data1")
    PLAYBOOK_PATH: str = os.getenv("PLAYBOOK_PATH", "")
    SYNC_PATH: str = os.getenv("SYNC_PATH", "")


settings = Settings()
