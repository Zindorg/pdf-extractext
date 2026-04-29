"""Infrastructure Layer - External adapters."""

from infrastructure.database_connection import close_connection, get_database
from infrastructure.database_setup import create_indexes, get_collection, setup_database

__all__ = [
    "get_database",
    "close_connection",
    "setup_database",
    "create_indexes",
    "get_collection",
]
