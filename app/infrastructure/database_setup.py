"""Database setup and index configuration for MongoDB."""

from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database

from app.infrastructure.database_connection import get_database


def create_indexes(db: Database = None) -> None:
    """Create all required indexes for the application."""
    database = db if db is not None else get_database()
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
    """Initialize database with proper configuration."""
    db = get_database()
    create_indexes(db)
    return db


def get_collection() -> Collection:
    """Get the pdf_documents collection from singleton connection."""
    return get_database()["pdf_documents"]
