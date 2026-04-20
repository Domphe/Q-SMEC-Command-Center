"""SQLModel database engine, session management, and initialization."""

from sqlmodel import Session, SQLModel, create_engine

from backend.config import settings

DATABASE_URL = "sqlite:///{}".format(settings.SQLITE_PATH)

engine = create_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False},
)


def get_session():
    """Yield a database session for FastAPI dependency injection."""
    with Session(engine) as session:
        yield session


def init_db():
    """Create all tables defined by SQLModel metadata."""
    # Import models so they register with SQLModel
    from backend.models import (  # noqa: F401
        AITask,
        Client,
        EmailCache,
        Note,
        PipelineStatus,
    )
    from backend.models.email_feedback import (  # noqa: F401
        EmailFeedback,
        LearnedSenderRule,
    )

    SQLModel.metadata.create_all(engine)
