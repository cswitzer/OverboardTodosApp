from typing import Generator, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLACHEMY_DATABASE_URL = "sqlite:///./todosapp.db"

# Creates a connection to the SQLite database with multithreading support.
engine = create_engine(
    SQLACHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Creates a new database session to interact with the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creates a base class for ORM models to inherit from
Base = declarative_base()


def get_db() -> Generator[Session, Any, None]:
    """Dependency to get the database session.

    Order of operations:
    1. gen = get_db()
    2. db = next(gen)
    3. gen.close()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
