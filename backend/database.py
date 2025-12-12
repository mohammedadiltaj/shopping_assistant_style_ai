"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os
from typing import Generator

# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql://shopping_user:shopping_pass@localhost:5432/shopping_db"
# )
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:shopping_pass@db.qcoblrkolhgmtzsnpclu.supabase.co:5432/postgres"
)

# Create engine with pgvector support
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=False,
    connect_args={"options": "-csearch_path=retail,public"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

