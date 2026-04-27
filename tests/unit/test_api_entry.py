"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

from api.routes.pdf_routes import router, get_pdf_service
from core.exceptions import InvalidFileException, PDFExtractionException
from models.pdf_document import PDFDocument


def create_test_app(mock_service=None):
    """Create FastAPI test app with mocked service."""
    app = FastAPI()

    if mock_service:
        def override_get_pdf_service():
            return mock_service

        app.dependency_overrides[get_pdf_service] = override_get_pdf_service

    app.include_router(router)
    return app


class TestUploadEndpoint:
    """Tests for upload endpoint."""

    def test_accepts_valid_pdf(self):
        """Should accept and process valid PDF upload."""
        mock_doc = PDFDocument(
            checksum="abc123checksum",
            id="abc123",
            filename="document.pdf",
            file_size=100,
            page_count=5,
            text_content="Extracted text",
        )
        mock_service = MagicMock()
        mock_service.process_pdf = AsyncMock(return_value=mock_doc)

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post(
            "/pdf/upload",
            files={"file": ("document.pdf", b"pdf content", "application/pdf")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "document.pdf"
        assert data["id"] == "abc123"

    def test_rejects_file_too_large(self):
        """Should reject files larger than max size."""
        from core.config import settings

        mock_service = MagicMock()
        app = create_test_app(mock_service)
        client = TestClient(app)

        large_content = b"x" * (settings.max_file_size + 1)

        response = client.post(
            "/pdf/upload",
            files={"file": ("large.pdf", large_content, "application/pdf")},
        )

        assert response.status_code == 413

    def test_returns_400_on_invalid_file(self):
        """Should return 400 for invalid files."""
        mock_service = MagicMock()
        mock_service.process_pdf = AsyncMock(
            side_effect=InvalidFileException("Invalid file")
        )

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post(
            "/pdf/upload",
            files={"file": ("invalid.txt", b"content", "text/plain")},
        )

        assert response.status_code == 400


class TestExtractEndpoint:
    """Tests for extract endpoint."""

    def test_extracts_from_existing_pdf(self):
        """Should extract text from existing PDF."""
        mock_doc = PDFDocument(
            checksum="abc123checksum",
            id="abc123",
            filename="document.pdf",
            text_content="Extracted text",
            page_count=5,
        )

        mock_service = MagicMock()
        mock_service.extract_text_from_pdf = AsyncMock(return_value=mock_doc)

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post("/pdf/abc123/extract")

        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Extracted text"

    def test_returns_404_for_nonexistent_pdf(self):
        """Should return 404 when PDF not found."""
        mock_service = MagicMock()
        mock_service.extract_text_from_pdf = AsyncMock(
            side_effect=PDFExtractionException("PDF not found")
        )

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post("/pdf/xyz789/extract")

        assert response.status_code == 404
