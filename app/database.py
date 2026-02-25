from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — yields a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def enable_extensions(db):
    """Enable PostGIS and pg_trgm. Called once at app startup."""
    db.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
    db.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
    db.commit()
