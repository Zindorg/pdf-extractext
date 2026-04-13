"""Pytest configuration and shared fixtures.

This module contains fixtures used across multiple test files,
following CLEAN CODE principles for test setup.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from services.pdf_service import PDFService
from repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface
from infrastructure.pdf_extractor_adapter import PDFExtractorAdapter
from api.routes.pdf_routes import router
from fastapi import FastAPI


@pytest.fixture
def mock_repository():
    """Create a mock PDF repository.

    Returns:
        MagicMock: Mocked repository interface.
    """
    mock = MagicMock(spec=PDFRepositoryInterface)
    mock.save = AsyncMock(return_value="/fake/path/test.pdf")
    mock.get = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_extractor():
    """Create a mock PDF extractor adapter.

    Returns:
        MagicMock: Mocked extractor adapter.
    """
    mock = MagicMock(spec=PDFExtractorAdapter)
    mock.extract_text = MagicMock(return_value=("Extracted text content", 5))
    mock.extract_text_from_page_range = MagicMock(return_value=("Page text", 2))
    return mock


@pytest.fixture
def pdf_service(mock_repository, mock_extractor):
    """Create PDFService with mocked dependencies.

    Args:
        mock_repository: Mocked repository fixture.
        mock_extractor: Mocked extractor fixture.

    Returns:
        PDFService: Service instance with mocked dependencies.
    """
    return PDFService(mock_repository, mock_extractor)


@pytest.fixture
def valid_pdf_content():
    """Provide valid PDF binary content.

    Returns:
        bytes: Sample PDF content for testing.
    """
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"


@pytest.fixture
def test_client():
    """Create FastAPI test client.

    Returns:
        TestClient: Client for testing API endpoints.
    """
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)
