"""Tests para RepositoryFactory."""

from unittest.mock import MagicMock, patch

import pytest

from app.repositories.repository_factory import RepositoryFactory


class TestRepositoryFactory:
    """Crear repository retorna instancia singleton."""

    def setup_method(self):
        """Reset factory before each test."""
        RepositoryFactory.reset()

    def test_get_pdf_repository_creates_singleton(self):
        mock_db = MagicMock()

        with patch("app.repositories.repository_factory.get_database", return_value=mock_db):
            with patch("app.repositories.repository_factory.MongoPDFRepository") as MockRepo:
                instance = MagicMock()
                MockRepo.return_value = instance
                result = RepositoryFactory.get_pdf_repository()
                assert result == instance
                assert result == RepositoryFactory.get_pdf_repository()

    def test_reset_clears_repository(self):
        """Reset permite crear nueva instancia."""
        mock_db = MagicMock()

        with patch("app.repositories.repository_factory.get_database", return_value=mock_db):
            with patch("app.repositories.repository_factory.MongoPDFRepository") as MockRepo:
                instance1 = MagicMock()
                MockRepo.return_value = instance1
                RepositoryFactory.get_pdf_repository()
                RepositoryFactory.reset()
                instance2 = MagicMock()
                MockRepo.return_value = instance2
                result = RepositoryFactory.get_pdf_repository()
                assert result == instance2

    def test_set_repository_overrides_instance(self):
        """Set repository permite inyectar mock."""
        mock_repo = MagicMock()
        RepositoryFactory.set_repository(mock_repo)
        result = RepositoryFactory.get_pdf_repository()
        assert result == mock_repo
