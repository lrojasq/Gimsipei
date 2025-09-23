from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from os import getenv
from dotenv import load_dotenv
from typing import Generator, Any

load_dotenv()

DATABASE_URL = f"mysql+pymysql://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@{getenv('DB_HOST')}:{getenv('DB_PORT')}/{getenv('DB_NAME')}"

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Enable connection health checks
    connect_args={
        "connect_timeout": 10,  # Connection timeout in seconds
        "read_timeout": 30,  # Read timeout in seconds
        "write_timeout": 30,  # Write timeout in seconds
    },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Session:
    """Get database session

    Returns:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
