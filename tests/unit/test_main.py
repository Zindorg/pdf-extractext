"""Tests para main.py: create_application y lifespan."""

import logging
from unittest.mock import MagicMock, patch

from app.config.settings import settings
from app.main import create_application, lifespan


class TestCreateApplication:
    def test_exposes_pdf_endpoints_under_api_v1(self):
        app = create_application()

        paths = set(app.openapi()["paths"])

        assert {
            "/api/v1/pdfs",
            "/api/v1/pdfs/{file_id}/text",
            "/api/v1/pdfs/{doc_id}/download",
            "/api/v1/pdfs/{doc_id}",
        } <= paths

    def test_title_comes_from_settings(self):
        assert create_application().title == settings.app_name


class TestLifespan:
    async def test_exposes_client_and_database_on_app_state(self):
        app = create_application()
        with patch("app.main.setup_database") as setup, patch("app.main.MongoClient") as client_cls:
            client = client_cls.return_value
            database = MagicMock(name="database")
            client.__getitem__.return_value = database

            async with lifespan(app):
                assert app.state.mongodb_client is client
                assert app.state.mongodb_database is database
                setup.assert_called_once_with(database)
                client.__getitem__.assert_called_once_with(settings.mongodb_database)

    async def test_closes_client_on_shutdown(self):
        app = create_application()
        with patch("app.main.setup_database"), patch("app.main.MongoClient") as client_cls:
            async with lifespan(app):
                client_cls.return_value.close.assert_not_called()

            client_cls.return_value.close.assert_called_once()

    async def test_repeated_startups_do_not_duplicate_log_handlers(self):
        app = create_application()
        before = len(logging.getLogger().handlers)
        with patch("app.main.setup_database"), patch("app.main.MongoClient"):
            for _ in range(3):
                async with lifespan(app):
                    pass

        assert len(logging.getLogger().handlers) <= before + 1
