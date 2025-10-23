from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create engine with explicit parameters
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Check connection before using
    echo=True  # Enable SQL logging to see what's happening
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()