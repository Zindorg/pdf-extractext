"""Tests para acceso a colecciones."""

from unittest.mock import MagicMock, patch
from pymongo.database import Database

import app.infrastructure.database_connection as db_conn

class TestProvidesAccessToCollection:
    """Provee acceso a coleccion pdf_documents."""

    def test_access_to_pdf_documents(self):
        mock_collection = MagicMock()
        mock_db = MagicMock(spec=Database)
        mock_db.__getitem__.return_value = mock_collection

        # Inyectamos el mock en get_database
        with patch.object(db_conn, "get_database", return_value=mock_db):
            db = db_conn.get_database()
            assert db["pdf_documents"] is mock_collection
