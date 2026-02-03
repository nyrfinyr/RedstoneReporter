"""MongoDB connection setup using Motor and Beanie."""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient = None

MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 3


async def connect_to_mongo():
    """Initialize MongoDB connection and Beanie ODM with retry logic."""
    global client
    from app.models import ALL_DOCUMENT_MODELS

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000,
            )
            db = client[settings.MONGODB_DB_NAME]
            await init_beanie(database=db, document_models=ALL_DOCUMENT_MODELS)
            logger.info(f"Connected to MongoDB: {settings.MONGODB_URI}/{settings.MONGODB_DB_NAME}")
            return
        except Exception as e:
            if attempt < MAX_RETRIES:
                logger.warning(
                    f"MongoDB connection attempt {attempt}/{MAX_RETRIES} failed: {e}. "
                    f"Retrying in {RETRY_DELAY_SECONDS}s..."
                )
                await asyncio.sleep(RETRY_DELAY_SECONDS)
            else:
                logger.error(f"MongoDB connection failed after {MAX_RETRIES} attempts: {e}")
                raise


async def close_mongo_connection():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")
