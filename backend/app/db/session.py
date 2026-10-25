from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    """Provide one database session per request and always close it afterwards."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
