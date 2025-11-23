from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from pymongo.server_api import ServerApi
from app.config import settings

_client: Optional[AsyncIOMotorClient] = None

def get_mongo_client() -> AsyncIOMotorClient:
    """Return the global motor client. Initialize lazily if needed."""
    global _client
    if _client is None:
        # Use newer Server API version and add connection options
        _client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            server_api=ServerApi('1'),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000
        )
    return _client

def close_mongo_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None

def get_mongo_db():
    """Get MongoDB database instance"""
    client = get_mongo_client()
    return client[settings.MONGODB_DATABASE]