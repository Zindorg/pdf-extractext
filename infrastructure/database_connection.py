"""Database connection singleton for MongoDB."""

from typing import Optional

from pymongo.database import Database
from pymongo.mongo_client import MongoClient

from core.config import settings

# Singleton state
_connection_state = {
    "client": None,
    "database": None,
}


def get_database() -> Database:
    """Get or create database connection (singleton).

    Returns:
        Configured MongoDB database instance

    Raises:
        ConnectionError: If cannot connect to MongoDB
    """
    if _connection_state["database"] is not None:
        return _connection_state["database"]

    client = MongoClient(settings.mongodb_uri)

    # Verify connection with ping
    client.admin.command("ping")

    db = client[settings.mongodb_database]

    _connection_state["client"] = client
    _connection_state["database"] = db

    return db


def close_connection() -> None:
    """Close database connection and reset singleton state."""
    if _connection_state["client"] is not None:
        _connection_state["client"].close()
        _connection_state["client"] = None
        _connection_state["database"] = None
