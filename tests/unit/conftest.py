"""Fixtures exclusivas para tests unitarios."""

from datetime import datetime
from unittest.mock import MagicMock, Mock

import pytest
from bson import ObjectId
from pymongo.database import Database
from pymongo.mongo_client import MongoClient

from app.infrastructure.database_connection import DatabaseConnection


@pytest.fixture(autouse=True)
def reset_database_singleton():
    """Resetea el singleton de DatabaseConnection antes de cada test."""
    DatabaseConnection._instance = None
    DatabaseConnection._client = None
    DatabaseConnection._database = None
    yield


@pytest.fixture
def mock_database():
    """Crea un mock de MongoDB (db, collection) listo para usar."""
    db = MagicMock()
    collection = MagicMock()
    db.__getitem__ = Mock(return_value=collection)
    db.pdf_documents = collection
    return db, collection


@pytest.fixture
def temp_file_repository(tmp_path, monkeypatch):
    """FilePDFRepository apuntando a un directorio temporal."""
    from app.config import Settings
    from app.repositories.file_pdf_repository import FilePDFRepository

    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    mock_settings = Settings(upload_dir=str(upload_dir))
    monkeypatch.setattr("app.repositories.file_pdf_repository.settings", mock_settings)
    return FilePDFRepository()
