"""Database setup and index configuration for MongoDB."""

from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database

from infrastructure.database_connection import get_database


def create_indexes(db: Database = None) -> None:
    """Create all required indexes for the application.

    Args:
        db: MongoDB database instance. If None, uses singleton.

    Example:
        >>> from infrastructure.database_setup import create_indexes
        >>> create_indexes()  # Crea índices en la BD por defecto
    """
    database = db or get_database()
    collection: Collection = database["pdf_documents"]

    # Unique index on checksum for duplicate detection
    collection.create_index(
        [("checksum", ASCENDING)],
        unique=True,
        name="idx_checksum_unique",
    )

    # Index for filtering active/deleted documents
    collection.create_index(
        [("deleted_at", ASCENDING)],
        name="idx_deleted_at",
    )

    # Index for chronological queries
    collection.create_index(
        [("created_at", DESCENDING)],
        name="idx_created_at_desc",
    )


def setup_database() -> Database:
    """Initialize database with proper configuration.

    Returns:
        Configured database instance from singleton.

    Example:
        >>> from infrastructure.database_setup import setup_database
        >>> db = setup_database()
        >>> # Database ready with indexes
    """
    db = get_database()
    create_indexes(db)
    return db


def get_collection() -> Collection:
    """Get the pdf_documents collection from singleton connection.

    Returns:
        Collection instance for pdf_documents.

    Example:
        >>> from infrastructure.database_setup import get_collection
        >>> collection = get_collection()
        >>> collection.insert_one({"checksum": "abc123"})
    """
    return get_database()["pdf_documents"]
