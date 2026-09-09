import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.models import Base

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
SessionLocal = None

if DATABASE_URL:
    # Ensure sync URL format for standard engine
    sync_db_url = DATABASE_URL
    if sync_db_url.startswith("postgresql+asyncpg://"):
        sync_db_url = sync_db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    connect_args = {"check_same_thread": False} if sync_db_url.startswith("sqlite") else {}
    engine = create_engine(sync_db_url, echo=False, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create database tables if engine is configured."""
    if engine:
        Base.metadata.create_all(bind=engine)


def get_db_session() -> Optional[Session]:
    """Retrieve an active database session if configured."""
    if SessionLocal:
        return SessionLocal()
    return None
