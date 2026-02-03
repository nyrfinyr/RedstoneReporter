"""Database configuration and setup."""

from app.database.connection import connect_to_mongo, close_mongo_connection

__all__ = ["connect_to_mongo", "close_mongo_connection"]
