from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./food_matcher.db"
SYNC_DATABASE_URL = "sqlite:///./food_matcher.db"

# Using sync engine for simplicity in MVP; can switch to async later
engine = create_engine(SYNC_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
