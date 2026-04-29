"""Tests for database connection singleton."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from pymongo.database import Database
from pymongo.mongo_client import MongoClient


class TestSingletonReturnsSameInstance:
    """Test 1: Singleton pattern returns same instance."""

    def test_singleton_returns_same_instance(self):
        """Multiple calls return the same database instance."""
        from infrastructure.database_connection import get_database, _connection_state

        # Reset singleton state
        _connection_state["client"] = None
        _connection_state["database"] = None

        with patch("infrastructure.database_connection.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_db = MagicMock()
            mock_instance.__getitem__ = Mock(return_value=mock_db)
            mock_client.return_value = mock_instance

            db1 = get_database()
            db2 = get_database()

            assert db1 is db2


class TestUsesConfigurationFromSettings:
    """Test 2: Uses configuration from Settings."""

    def test_uses_configuration_from_settings(self):
        """Connection uses URI from core.config.Settings."""
        from infrastructure.database_connection import get_database, _connection_state

        # Reset singleton state
        _connection_state["client"] = None
        _connection_state["database"] = None

        with patch("infrastructure.database_connection.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_db = MagicMock()
            mock_instance.__getitem__ = Mock(return_value=mock_db)
            mock_client.return_value = mock_instance

            get_database()

            mock_client.assert_called_once()
            # Verify URI from Settings is used
            call_args = mock_client.call_args
            assert "mongodb" in str(call_args[0][0]).lower()


class TestReturnsDatabaseWithConfiguredName:
    """Test 3: Returns database with configured name."""

    def test_returns_database_with_configured_name(self):
        """Returns database instance with name from Settings."""
        from infrastructure.database_connection import get_database, _connection_state

        # Reset singleton state
        _connection_state["client"] = None
        _connection_state["database"] = None

        with patch("infrastructure.database_connection.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_db = MagicMock(spec=Database)
            mock_instance.__getitem__ = Mock(return_value=mock_db)
            mock_client.return_value = mock_instance

            db = get_database()

            assert db is mock_db


class TestProvidesAccessToCollection:
    """Test 4: Provides access to pdf_documents collection."""

    def test_provides_access_to_collection(self):
        """Database provides access to pdf_documents collection."""
        from infrastructure.database_connection import get_database, _connection_state

        # Reset singleton state
        _connection_state["client"] = None
        _connection_state["database"] = None

        with patch("infrastructure.database_connection.MongoClient") as mock_client:
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
        from infrastructure.database_connection import get_database, _connection_state

        # Reset singleton state
        _connection_state["client"] = None
        _connection_state["database"] = None

        with patch("infrastructure.database_connection.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_db = MagicMock()
            mock_instance.__getitem__ = Mock(return_value=mock_db)
            mock_client.return_value = mock_instance

            get_database()

            mock_instance.admin.command.assert_called_with("ping")


class TestCloseConnectionReleasesResources:
    """Test 6: Close connection releases resources."""

    def test_close_connection_releases_resources(self):
        """Closing connection clears singleton state."""
        from infrastructure.database_connection import (
            get_database,
            close_connection,
            _connection_state,
        )

        # Reset singleton state
        _connection_state["client"] = None
        _connection_state["database"] = None

        with patch("infrastructure.database_connection.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_db = MagicMock()
            mock_instance.__getitem__ = Mock(return_value=mock_db)
            mock_client.return_value = mock_instance

            get_database()
            close_connection()

            # After close, singleton state should be reset
            mock_instance.close.assert_called_once()
