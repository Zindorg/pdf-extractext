"""Tests para verificacion de conexion."""

from unittest.mock import patch

from app.infrastructure.database_connection import DatabaseConnection
from tests.unit.infrastructure.database_connection._mock_mongo_client import _mock_mongo_client


class TestVerifiesConnectionOnCreation:
    """Verifica conexion al crear."""

    def test_verifies_connection(self):
        with patch(
            "app.infrastructure.database_connection.MongoClient"
        ) as mock_client:
            mock_instance, _ = _mock_mongo_client(mock_client)
            DatabaseConnection().connect()
            mock_instance.admin.command.assert_called_with("ping")
