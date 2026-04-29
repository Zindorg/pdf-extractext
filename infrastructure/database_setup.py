"""Database setup and index configuration for MongoDB."""

from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.mongo_client import MongoClient


def create_indexes(db: Database) -> None:
    """Create all required indexes for the application.

    Args:
        db: MongoDB database instance
    """
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


def setup_database(mongo_uri: str, database_name: str = "pdf_extractext") -> Database:
    """Initialize database with proper configuration.

    Args:
        mongo_uri: MongoDB connection URI
        database_name: Name of the database

    Returns:
        Configured database instance
    """
    client: MongoClient = MongoClient(mongo_uri)
    db: Database = client[database_name]

    create_indexes(db)

    return db


def get_collection(db: Database) -> Collection:
    """Get the pdf_documents collection.

    Args:
        db: MongoDB database instance

    Returns:
        Collection instance for pdf_documents
    """
    return db["pdf_documents"]
