"""Database setup and index configuration for MongoDB."""

import logging

from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database

logger = logging.getLogger(__name__)


def create_indexes(db: Database) -> None:
    """Create all required indexes for the application."""
    collection: Collection = db["pdf_documents"]

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

    logger.info("Database indexes created successfully")


def setup_database(db: Database) -> Database:
    """Initialize database with proper configuration."""
    logger.info("Setting up database")
    create_indexes(db)
    return db
