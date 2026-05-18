"""Database connection singleton using class-based approach."""

from typing import Optional

from pymongo.database import Database
from pymongo.mongo_client import MongoClient

from app.config.settings import settings
from app.exceptions import DatabaseConnectionException


class DatabaseConnection:
    """Singleton database connection manager."""

    _instance: Optional["DatabaseConnection"] = None
    _client: Optional[MongoClient] = None
    _database: Optional[Database] = None

    def __new__(cls) -> "DatabaseConnection":
        """Create or return singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self) -> Database:
        """Get or create database connection."""
        if self._database is not None:
            return self._database

        try:
            self._client = MongoClient(settings.mongodb_uri)
            self._client.admin.command("ping")
            self._database = self._client[settings.mongodb_database]
            return self._database
        except Exception as e:
            raise DatabaseConnectionException(
                f"Failed to connect to MongoDB: {e}"
            ) from e

    def close(self) -> None:
        """Close database connection and reset singleton state."""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._database = None
            DatabaseConnection._instance = None

    @property
    def is_connected(self) -> bool:
        """Check if database connection is active."""
        return self._database is not None and self._client is not None


# Module-level singleton for direct access
_connection: DatabaseConnection | None = None


def get_database() -> Database:
    """Get database instance from singleton."""
    global _connection
    if _connection is None:
        _connection = DatabaseConnection()
    return _connection.connect()


def close_connection() -> None:
    """Close database connection."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None
