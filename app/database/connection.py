"""MongoDB connection setup using Motor and Beanie."""

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient = None


async def connect_to_mongo():
    """Initialize MongoDB connection and Beanie ODM."""
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]

    from app.models import ALL_DOCUMENT_MODELS

    await init_beanie(database=db, document_models=ALL_DOCUMENT_MODELS)
    logger.info(f"Connected to MongoDB: {settings.MONGODB_URI}/{settings.MONGODB_DB_NAME}")


async def close_mongo_connection():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")
