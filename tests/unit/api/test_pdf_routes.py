"""Tests para endpoints de la API (capa de presentación)."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from app.exceptions import InvalidFileException, PDFExtractionException, PDFNotFoundException
from app.models.pdf_document import PDFDocument
from app.routes.pdf_routes import get_pdf_service, router


@pytest.fixture
def mock_service():
    """Servicio mockeado por defecto."""
    return MagicMock()


@pytest.fixture
def test_client(mock_service):
    """Crea un TestClient de FastAPI con el servicio mockeado inyectado."""
    app = FastAPI()
    app.dependency_overrides[get_pdf_service] = lambda: mock_service
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def sample_document() -> PDFDocument:
    return PDFDocument(
        checksum="abc123checksum",
        id="abc123",
        filename="document.pdf",
        file_size=100,
        page_count=5,
        text_content="Extracted text",
    )


class TestUploadEndpoint:
    """Tests para POST /pdf/upload."""

    def test_accepts_valid_pdf(self, test_client, mock_service, sample_document):
        mock_service.generate_checksum.return_value = "abc123checksum"
        mock_service.find_by_checksum.return_value = None
        mock_service.process_pdf = AsyncMock(return_value=sample_document)

        response = test_client.post(
            "/pdf/upload",
            files={"file": ("document.pdf", b"pdf content", "application/pdf")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "document.pdf"
        assert data["id"] == "abc123"

    def test_rejects_file_too_large(self, test_client):
        from app.config.settings import settings

        large_content = b"x" * (settings.max_file_size + 1)
        response = test_client.post(
            "/pdf/upload",
            files={"file": ("large.pdf", large_content, "application/pdf")},
        )
        assert response.status_code == 422

    def test_returns_422_on_invalid_file(self, test_client, mock_service):
        mock_service.process_pdf = AsyncMock(
            side_effect=InvalidFileException("Invalid file")
        )
        response = test_client.post(
            "/pdf/upload",
            files={"file": ("invalid.txt", b"content", "text/plain")},
        )
        assert response.status_code == 422


class TestExtractEndpoint:
    """Tests para POST /pdf/{id}/extract."""

    def test_extracts_from_existing_pdf(self, test_client, mock_service, sample_document):
        mock_service.extract_text_from_pdf = AsyncMock(return_value=sample_document)

        response = test_client.post("/pdf/abc123/extract")

        assert response.status_code == 200
        assert response.json()["text"] == "Extracted text"

    def test_returns_404_for_nonexistent_pdf(self, test_client, mock_service):
        mock_service.extract_text_from_pdf = AsyncMock(
            side_effect=PDFNotFoundException("PDF not found")
        )

        response = test_client.post("/pdf/xyz789/extract")
        assert response.status_code == 404
