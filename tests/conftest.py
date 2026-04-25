"""Pytest configuration and shared fixtures."""

from pathlib import Path

import pytest
from unittest.mock import AsyncMock, MagicMock

from services.pdf_service import PDFService
from repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface


@pytest.fixture
def mock_repository():
    """Create a mock PDF repository."""
    mock = MagicMock(spec=PDFRepositoryInterface)
    mock.save = AsyncMock(return_value=None)
    mock.get = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def pdf_service(mock_repository):
    """Create PDFService with mocked repository."""
    return PDFService(mock_repository)


@pytest.fixture
def valid_pdf_content():
    """Provide valid PDF binary content from fixtures."""
    fixture_path = Path(__file__).parent / "fixtures" / "valid.pdf"
    return fixture_path.read_bytes()
