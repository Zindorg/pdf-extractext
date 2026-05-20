"""Tests para fallo de conexion."""

from unittest.mock import patch

import pytest

from app.exceptions import DatabaseConnectionException
from app.infrastructure.database_connection import DatabaseConnection


class TestConnectionFailure:
    """Fallo de conexion lanza exception."""

    def test_raises_exception_on_failure(self):
        with patch(
            "app.infrastructure.database_connection.MongoClient"
        ) as mock_client:
            mock_client.side_effect = Exception("Connection refused")
            with pytest.raises(DatabaseConnectionException) as exc_info:
                DatabaseConnection().connect()
            assert "Failed to connect to MongoDB" in str(exc_info.value)
