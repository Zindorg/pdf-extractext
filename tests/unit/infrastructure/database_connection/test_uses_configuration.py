"""Tests para configuracion de DatabaseConnection."""

from unittest.mock import patch

from app.infrastructure.database_connection import DatabaseConnection
from tests.unit.infrastructure.database_connection._mock_mongo_client import _mock_mongo_client


class TestUsesConfigurationFromSettings:
    """Usa configuracion desde Settings."""

    def test_uses_configuration(self):
        with patch(
            "app.infrastructure.database_connection.MongoClient"
        ) as mock_client:
            _mock_mongo_client(mock_client)
            DatabaseConnection().connect()
            mock_client.assert_called_once()
            assert "mongodb" in str(mock_client.call_args[0][0]).lower()
