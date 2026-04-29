"""Database connection singleton using class-based approach."""

from typing import Optional

from pymongo.database import Database
from pymongo.mongo_client import MongoClient

from core.config import settings
from core.exceptions import DatabaseConnectionException


class DatabaseConnection:
    """Singleton database connection manager.

    Esta clase gestiona la conexión a MongoDB como un singleton,
    asegurando que solo exista una instancia de conexión activa
    durante toda la vida de la aplicación.

    Example:
        >>> db = DatabaseConnection().connect()
        >>> collection = db["pdf_documents"]
        >>> DatabaseConnection().close()
    """

    _instance: Optional["DatabaseConnection"] = None
    _client: Optional[MongoClient] = None
    _database: Optional[Database] = None

    def __new__(cls) -> "DatabaseConnection":
        """Crear o retornar instancia singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self) -> Database:
        """Get or create database connection.

        Returns:
            Configured MongoDB database instance.

        Raises:
            DatabaseConnectionException: If cannot connect to MongoDB.
        """
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


# Global singleton instance for backward compatibility
_connection = DatabaseConnection()


def get_database() -> Database:
    """Get database instance from singleton.

    Returns:
        Configured MongoDB database instance.

    Example:
        >>> db = get_database()
        >>> collection = db["pdf_documents"]
    """
    return _connection.connect()


def close_connection() -> None:
    """Close database connection.

    Example:
        >>> close_connection()
        >>> # Connection is now closed
    """
    _connection.close()
