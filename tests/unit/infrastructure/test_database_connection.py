"""Tests para DatabaseConnection (patrón Singleton)."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from pymongo.database import Database

from app.exceptions import DatabaseConnectionException
from app.infrastructure.database_connection import DatabaseConnection, get_database


def _mock_mongo_client(mock_client_cls):
    """Crea y configura un mock completo de MongoClient; retorna (mock_instance, mock_db)."""
    mock_instance = MagicMock()
    mock_instance.admin.command.return_value = {"ok": 1}
    mock_db = MagicMock(spec=Database)
    mock_instance.__getitem__ = Mock(return_value=mock_db)
    mock_client_cls.return_value = mock_instance
    return mock_instance, mock_db


class TestSingletonReturnsSameInstance:
    def test_singleton_returns_same_instance(self):
        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            _mock_mongo_client(mock_client)
            db1 = DatabaseConnection().connect()
            db2 = DatabaseConnection().connect()
            assert db1 is db2


class TestUsesConfigurationFromSettings:
    def test_uses_configuration_from_settings(self):
        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            _mock_mongo_client(mock_client)
            DatabaseConnection().connect()
            mock_client.assert_called_once()
            assert "mongodb" in str(mock_client.call_args[0][0]).lower()


class TestReturnsDatabaseWithConfiguredName:
    def test_returns_database_with_configured_name(self):
        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            _, mock_db = _mock_mongo_client(mock_client)
            db = DatabaseConnection().connect()
            assert db is mock_db


class TestProvidesAccessToCollection:
    def test_provides_access_to_pdf_documents_collection(self):
        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            mock_collection = MagicMock()
            mock_db = MagicMock(spec=Database)
            mock_db.__getitem__ = Mock(return_value=mock_collection)
            mock_instance = MagicMock()
            mock_instance.admin.command.return_value = {"ok": 1}
            mock_instance.__getitem__ = Mock(return_value=mock_db)
            mock_client.return_value = mock_instance

            db = get_database()
            assert db["pdf_documents"] is mock_collection


class TestVerifiesConnectionOnCreation:
    def test_verifies_connection_on_creation(self):
        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            mock_instance, _ = _mock_mongo_client(mock_client)
            DatabaseConnection().connect()
            mock_instance.admin.command.assert_called_with("ping")


class TestCloseConnectionReleasesResources:
    def test_close_connection_releases_resources(self):
        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            mock_instance, _ = _mock_mongo_client(mock_client)
            connection = DatabaseConnection()
            connection.connect()
            connection.close()
            mock_instance.close.assert_called_once()


class TestConnectionFailure:
    def test_raises_database_connection_exception_on_failure(self):
        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            mock_client.side_effect = Exception("Connection refused")
            with pytest.raises(DatabaseConnectionException) as exc_info:
                DatabaseConnection().connect()
            assert "Failed to connect to MongoDB" in str(exc_info.value)


class TestIsConnectedProperty:
    def test_is_connected_reflects_state(self):
        with patch("app.infrastructure.database_connection.MongoClient") as mock_client:
            _mock_mongo_client(mock_client)
            connection = DatabaseConnection()
            assert connection.is_connected is False
            connection.connect()
            assert connection.is_connected is True
            connection.close()
            assert connection.is_connected is False
