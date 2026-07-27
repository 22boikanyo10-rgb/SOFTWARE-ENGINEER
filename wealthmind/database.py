"""Database connection and session management."""

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

from wealthmind.config import settings
from wealthmind.models import Base

logger = logging.getLogger(__name__)


def get_engine():
    """Create and return database engine."""
    kwargs = {
        "echo": settings.database_echo,
        "pool_size": settings.database_pool_size,
        "max_overflow": settings.database_max_overflow,
    }
    
    # Use in-memory SQLite for testing
    if settings.database_url.startswith("sqlite"):
        if settings.database_url == "sqlite:///:memory:":
            kwargs["connect_args"] = {"check_same_thread": False}
            kwargs["poolclass"] = StaticPool
    
    engine = create_engine(settings.database_url, **kwargs)
    
    # Log SQL queries in debug mode
    if settings.debug:
        @event.listens_for(Engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            logger.debug(f"SQL: {statement}")
    
    return engine


# Create engine
engine = get_engine()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def drop_db():
    """Drop all tables (for testing)."""
    Base.metadata.drop_all(bind=engine)
    logger.warning("Database dropped")


def get_db() -> Session:
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
