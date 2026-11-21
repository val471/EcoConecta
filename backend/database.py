import os
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _url() -> str:
    url = os.getenv("DATABASE_URL", "")
    # Render entrega postgres://... y SQLAlchemy con Psycopg 3 necesita postgresql+psycopg://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = _url()
engine = create_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None
SessionLocal = sessionmaker(bind=engine, autoflush=False) if engine else None
Base = declarative_base()


def ahora() -> datetime:
    return datetime.now(timezone.utc)


def get_db():
    if SessionLocal is None:
        raise RuntimeError("Falta la variable DATABASE_URL")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
