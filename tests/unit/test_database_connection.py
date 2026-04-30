"""Tests for database connection class-based singleton."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from pymongo.database import Database
from pymongo.mongo_client import MongoClient

from app.exceptions import DatabaseConnectionException


class TestSingletonReturnsSameInstance:
    """Test 1: Singleton pattern returns same instance."""

    def test_singleton_returns_same_instance(self):
        """Multiple calls return the same database instance."""
        from app.infrastructure.database_connection import DatabaseConnection

        # Reset singleton for test
        DatabaseConnection._instance = None
        DatabaseConnection._client = None
        DatabaseConnection._database = None

        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_db = MagicMock(spec=Database)
            mock_instance.__getitem__ = Mock(return_value=mock_db)
            mock_client.return_value = mock_instance

            connection = DatabaseConnection()
            db1 = connection.connect()
            db2 = connection.connect()

            assert db1 is db2


class TestUsesConfigurationFromSettings:
    """Test 2: Uses configuration from Settings."""

    def test_uses_configuration_from_settings(self):
        """Connection uses URI from core.config.Settings."""
        from app.infrastructure.database_connection import DatabaseConnection

        # Reset singleton for test
        DatabaseConnection._instance = None
        DatabaseConnection._client = None
        DatabaseConnection._database = None

        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_db = MagicMock()
            mock_instance.__getitem__ = Mock(return_value=mock_db)
            mock_client.return_value = mock_instance

            connection = DatabaseConnection()
            connection.connect()

            mock_client.assert_called_once()
            call_args = mock_client.call_args
            assert "mongodb" in str(call_args[0][0]).lower()


class TestReturnsDatabaseWithConfiguredName:
    """Test 3: Returns database with configured name."""

    def test_returns_database_with_configured_name(self):
        """Returns database instance with name from Settings."""
        from app.infrastructure.database_connection import DatabaseConnection

        # Reset singleton for test
        DatabaseConnection._instance = None
        DatabaseConnection._client = None
        DatabaseConnection._database = None

        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_db = MagicMock(spec=Database)
            mock_instance.__getitem__ = Mock(return_value=mock_db)
            mock_client.return_value = mock_instance

            connection = DatabaseConnection()
            db = connection.connect()

            assert db is mock_db


class TestProvidesAccessToCollection:
    """Test 4: Provides access to pdf_documents collection."""

    def test_provides_access_to_collection(self):
        """Database provides access to pdf_documents collection."""
        from app.infrastructure.database_connection import get_database
        from app.infrastructure.database_connection import DatabaseConnection

        # Reset singleton for test
        DatabaseConnection._instance = None
        DatabaseConnection._client = None
        DatabaseConnection._database = None

        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_db = MagicMock(spec=Database)
            mock_collection = MagicMock()
            mock_db.__getitem__ = Mock(return_value=mock_collection)
            mock_instance.__getitem__ = Mock(return_value=mock_db)
            mock_client.return_value = mock_instance

            db = get_database()
            collection = db["pdf_documents"]

            assert collection is mock_collection


class TestVerifiesConnectionOnCreation:
    """Test 5: Verifies connection on creation."""

    def test_verifies_connection_on_creation(self):
        """Ping is sent to verify connection when creating client."""
        from app.infrastructure.database_connection import DatabaseConnection

        # Reset singleton for test
        DatabaseConnection._instance = None
        DatabaseConnection._client = None
        DatabaseConnection._database = None

        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_db = MagicMock()
            mock_instance.__getitem__ = Mock(return_value=mock_db)
            mock_client.return_value = mock_instance

            connection = DatabaseConnection()
            connection.connect()

            mock_instance.admin.command.assert_called_with("ping")


class TestCloseConnectionReleasesResources:
    """Test 6: Close connection releases resources."""

    def test_close_connection_releases_resources(self):
        """Closing connection clears singleton state."""
        from app.infrastructure.database_connection import DatabaseConnection

        # Reset singleton for test
        DatabaseConnection._instance = None
        DatabaseConnection._client = None
        DatabaseConnection._database = None

        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_db = MagicMock()
            mock_instance.__getitem__ = Mock(return_value=mock_db)
            mock_client.return_value = mock_instance

            connection = DatabaseConnection()
            connection.connect()
            connection.close()

            mock_instance.close.assert_called_once()


class TestConnectionFailure:
    """Test 7: Connection failures are handled gracefully."""

    def test_raises_database_connection_exception_on_failure(self):
        """Raises DatabaseConnectionException when connection fails."""
        from app.infrastructure.database_connection import DatabaseConnection

        # Reset singleton for test
        DatabaseConnection._instance = None
        DatabaseConnection._client = None
        DatabaseConnection._database = None

        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            mock_client.side_effect = Exception("Connection refused")

            connection = DatabaseConnection()

            with pytest.raises(DatabaseConnectionException) as exc_info:
                connection.connect()

            assert "Failed to connect to MongoDB" in str(exc_info.value)


class TestIsConnectedProperty:
    """Test 8: is_connected property reflects connection state."""

    def test_is_connected_returns_true_when_connected(self):
        """is_connected returns True when database is connected."""
        from app.infrastructure.database_connection import DatabaseConnection

        # Reset singleton for test
        DatabaseConnection._instance = None
        DatabaseConnection._client = None
        DatabaseConnection._database = None

        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_db = MagicMock()
            mock_instance.__getitem__ = Mock(return_value=mock_db)
            mock_client.return_value = mock_instance

            connection = DatabaseConnection()
            assert connection.is_connected is False

            connection.connect()
            assert connection.is_connected is True

            connection.close()
            assert connection.is_connected is False
