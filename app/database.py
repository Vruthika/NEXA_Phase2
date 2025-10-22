from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
import redis
from app.config import settings

# PostgreSQL Database
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB
mongo_client = MongoClient(settings.MONGODB_URL)
mongodb = mongo_client.nexa_cms

# Redis
redis_client = redis.from_url(settings.REDIS_URL)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()