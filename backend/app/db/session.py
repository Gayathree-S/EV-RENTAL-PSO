"""
SQLAlchemy database session setup.
Engine points to backend/data/app.db (resolved absolutely so it works
regardless of where uvicorn is launched from).
"""

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Resolve db path relative to THIS file: db/ -> app/ -> backend/ -> data/
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_DB_PATH = _BACKEND_DIR / "data" / "app.db"

DATABASE_URL = f"sqlite:///{_DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # required for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yield a database session, always close after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
