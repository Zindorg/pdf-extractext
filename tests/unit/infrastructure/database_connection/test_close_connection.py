"""Tests para cierre de conexion."""

from unittest.mock import patch

from app.infrastructure.database_connection import DatabaseConnection
from tests.unit.infrastructure.database_connection._mock_mongo_client import _mock_mongo_client


class TestCloseConnectionReleasesResources:
    """Cierre libera recursos."""

    def test_closes_connection(self):
        with patch(
            "app.infrastructure.database_connection.MongoClient"
        ) as mock_client:
            mock_instance, _ = _mock_mongo_client(mock_client)
            connection = DatabaseConnection()
            connection.connect()
            connection.close()
            mock_instance.close.assert_called_once()
