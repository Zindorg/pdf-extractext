"""Tests para acceso a colecciones."""

from unittest.mock import MagicMock, Mock, patch
from pymongo.database import Database

from app.infrastructure.database_connection import get_database


class TestProvidesAccessToCollection:
    """Provee acceso a coleccion pdf_documents."""

    def test_access_to_pdf_documents(self):
        with patch(
            "app.infrastructure.database_connection.MongoClient"
        ) as mock_client:
            mock_collection = MagicMock()
            mock_db = MagicMock(spec=Database)
            mock_db.__getitem__ = Mock(return_value=mock_collection)
            mock_instance = MagicMock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_instance.__getitem__ = Mock(return_value=mock_db)
            mock_client.return_value = mock_instance

            db = get_database()
            assert db["pdf_documents"] is mock_collection
