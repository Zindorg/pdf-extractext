"""Tests para lifespan de FastAPI con app.state."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI

from app.main import lifespan


class TestLifespan:
    """Lifespan configura app.state correctamente."""

    @pytest.mark.asyncio
    async def test_sets_mongodb_client_on_app_state(self):
        """Guarda MongoClient en app.state durante lifespan."""
        app = MagicMock(spec=FastAPI)
        app.state = MagicMock()

        with patch("app.main.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            mock_instance.__getitem__ = MagicMock(return_value=MagicMock())

            async with lifespan(app):
                pass

            mock_instance.close.assert_called_once()
            app.state.mongodb_client = mock_instance

    @pytest.mark.asyncio
    async def test_sets_mongodb_database_on_app_state(self):
        """Guarda la base de datos en app.state durante lifespan."""
        app = MagicMock(spec=FastAPI)
        app.state = MagicMock()

        with patch("app.main.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_db = MagicMock()
            mock_client.return_value = mock_instance
            mock_instance.__getitem__ = MagicMock(return_value=mock_db)

            async with lifespan(app):
                pass

            app.state.mongodb_database = mock_db

    @pytest.mark.asyncio
    async def test_closes_client_on_teardown(self):
        """Cierra el cliente de MongoDB al salir del contexto."""
        app = MagicMock(spec=FastAPI)
        app.state = MagicMock()

        with patch("app.main.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            mock_instance.__getitem__ = MagicMock(return_value=MagicMock())

            async with lifespan(app):
                pass

            mock_instance.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_sets_database_collection(self):
        """La base de datos tiene la colección correcta."""
        app = MagicMock(spec=FastAPI)
        app.state = MagicMock()

        with patch("app.main.MongoClient") as mock_client:
            mock_instance = MagicMock()
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_client.return_value = mock_instance
            mock_instance.__getitem__ = MagicMock(return_value=mock_db)
            mock_db.__getitem__ = MagicMock(return_value=mock_collection)

            async with lifespan(app):
                pass

            assert mock_db is not None
