"""Tests para main.py (create_application y lifespan)."""

from unittest.mock import MagicMock, patch

import pytest

from app.main import create_application, lifespan


class TestCreateApplication:
    """Crear aplicacion retorna instancia FastAPI configurada."""

    def test_returns_fastapi_instance(self):
        app = create_application()
        assert app is not None

    def test_includes_router(self):
        app = create_application()
        routes = [route.path for route in app.routes]
        assert any("/api/v1/pdfs" in str(r) for r in routes)

    def test_title_and_version(self):
        app = create_application()
        assert "extract" in app.title.lower() or "PDF" in app.title
        assert app.version == "1.0.0"


class TestLifespan:
    """Lifespan llama setup correctamente."""

    async def test_setup_and_teardown(self):
        with patch("app.main.setup_database") as mock_setup:
            with patch("app.main.MongoClient"):
                app = create_application()
                async with lifespan(app):
                    pass
                mock_setup.assert_called_once()

    async def test_sets_app_state(self):
        """Lifespan configura app.state correctamente."""
        with patch("app.main.setup_database"):
            with patch("app.main.MongoClient") as mock_client:
                mock_instance = MagicMock()
                mock_db = MagicMock()
                mock_client.return_value = mock_instance
                mock_instance.__getitem__ = MagicMock(return_value=mock_db)

                app = create_application()
                async with lifespan(app):
                    pass

                assert hasattr(app.state, "mongodb_client")
                assert hasattr(app.state, "mongodb_database")
