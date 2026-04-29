"""Pytest configuration and shared fixtures."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface
from repositories.repository_factory import RepositoryFactory
from services.pdf_service import PDFService


@pytest.fixture
def mock_repository():
    """Create a mock PDF repository with all CRUD methods."""
    mock = MagicMock(spec=PDFRepositoryInterface)
    # CRUD operations
    mock.create = MagicMock(return_value=None)
    mock.find_by_id = MagicMock(return_value=None)
    mock.find_by_checksum = MagicMock(return_value=None)
    mock.find_all = MagicMock(return_value=[])
    mock.update = MagicMock(return_value=None)
    mock.soft_delete = MagicMock(return_value=False)
    mock.delete_by_id = MagicMock(return_value=False)
    mock.restore = MagicMock(return_value=False)
    return mock


@pytest.fixture
def mock_repository_with_duplicate(mock_repository):
    """Mock repository that simulates duplicate detection."""
    from models.pdf_document import PDFDocument

    existing_doc = PDFDocument(
        id="507f1f77bcf86cd799439011",
        checksum="duplicate_checksum",
        filename="existing.pdf",
        text_content="Existing content",
    )
    mock_repository.find_by_checksum.return_value = existing_doc
    return mock_repository


@pytest.fixture
def pdf_service(mock_repository):
    """Create PDFService with mocked repository."""
    return PDFService(repository=mock_repository)


@pytest.fixture
def reset_repository_factory():
    """Reset repository factory before and after test."""
    RepositoryFactory.reset()
    yield
    RepositoryFactory.reset()


@pytest.fixture
def valid_pdf_content():
    """Provide valid PDF binary content from fixtures."""
    fixture_path = Path(__file__).parent / "fixtures" / "valid.pdf"
    if fixture_path.exists():
        return fixture_path.read_bytes()
    # Return minimal PDF content if fixture doesn't exist
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"


@pytest.fixture
def sample_pdf_document():
    """Provide a sample PDFDocument for testing."""
    from models.pdf_document import PDFDocument

    return PDFDocument(
        id="507f1f77bcf86cd799439011",
        checksum="abc123checksum",
        filename="test.pdf",
        text_content="Sample text content",
        page_count=5,
        file_size=1024,
        content_type="application/pdf",
    )
