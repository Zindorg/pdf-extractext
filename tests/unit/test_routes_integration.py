"""Integration tests for all API endpoints (TDD)."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.routes.pdf_routes import router, get_pdf_service, set_pdf_repository
from app.exceptions import PDFNotFoundException, DuplicateDocumentException, InvalidFileException
from app.models.pdf_document import PDFDocument
from app.repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface
from datetime import datetime


@pytest.fixture
def mock_service():
    """Create a fully mocked PDFService."""
    return MagicMock()


def create_test_app(mock_service=None):
    """Create FastAPI test app with dependency injection override."""
    app = FastAPI()

    if mock_service:
        def override_get_pdf_service():
            return mock_service
        app.dependency_overrides[get_pdf_service] = override_get_pdf_service

    app.include_router(router)
    return app


def _make_document(**overrides):
    """Helper to create a PDFDocument with sensible defaults."""
    defaults = dict(
        id="507f1f77bcf86cd799439011",
        checksum="abc123checksum",
        filename="document.pdf",
        text_content="Extracted text content from PDF",
        page_count=5,
        file_size=1024,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    defaults.update(overrides)
    return PDFDocument(**defaults)


class TestUploadEndpoint:
    """POST /pdf/upload"""

    def test_upload_new_pdf_returns_200_with_data(self):
        """Uploading a new valid PDF returns 200 with document data."""
        doc = _make_document()
        mock_svc = MagicMock()
        mock_svc.generate_checksum.return_value = "checksum123"
        mock_svc.find_by_checksum.return_value = None
        mock_svc.process_pdf = AsyncMock(return_value=doc)

        client = TestClient(create_test_app(mock_svc))
        resp = client.post(
            "/pdf/upload",
            files={"file": ("doc.pdf", b"%pdf content", "application/pdf")},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["filename"] == "document.pdf"
        assert body["id"] == "507f1f77bcf86cd799439011"
        assert body["is_duplicate"] is False
        assert body["checksum"] == "abc123checksum"

    def test_upload_duplicate_returns_existing_with_flag_true(self):
        """Uploading a duplicate PDF returns existing doc with is_duplicate=True."""
        existing = _make_document()
        mock_svc = MagicMock()
        mock_svc.generate_checksum.return_value = "same_checksum"
        mock_svc.find_by_checksum.return_value = existing

        client = TestClient(create_test_app(mock_svc))
        resp = client.post(
            "/pdf/upload",
            files={"file": ("doc.pdf", b"same content", "application/pdf")},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["is_duplicate"] is True
        assert body["id"] == existing.id

    def test_upload_rejects_non_pdf_content_type(self):
        """Uploading a non-PDF file returns 422."""
        mock_svc = MagicMock()
        client = TestClient(create_test_app(mock_svc))
        resp = client.post(
            "/pdf/upload",
            files={"file": ("image.png", b"png data", "image/png")},
        )
        assert resp.status_code == 422

    def test_upload_rejects_empty_file(self):
        """Uploading an empty file returns 422."""
        mock_svc = MagicMock()
        client = TestClient(create_test_app(mock_svc))
        resp = client.post(
            "/pdf/upload",
            files={"file": ("empty.pdf", b"", "application/pdf")},
        )
        assert resp.status_code == 422


class TestListPdfsEndpoint:
    """GET /pdf"""

    def test_list_empty_returns_empty_list(self):
        """When no documents exist, returns empty list."""
        mock_svc = MagicMock()
        mock_svc.find_all.return_value = []

        client = TestClient(create_test_app(mock_svc))
        resp = client.get("/pdf")

        assert resp.status_code == 200
        body = resp.json()
        assert body["documents"] == []
        assert body["total"] == 0

    def test_list_with_documents_returns_all(self):
        """Returns all persisted documents."""
        docs = [
            _make_document(id="id1", filename="a.pdf", checksum="c1"),
            _make_document(id="id2", filename="b.pdf", checksum="c2"),
        ]
        mock_svc = MagicMock()
        mock_svc.find_all.return_value = docs

        client = TestClient(create_test_app(mock_svc))
        resp = client.get("/pdf")

        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 2
        filenames = [d["filename"] for d in body["documents"]]
        assert "a.pdf" in filenames
        assert "b.pdf" in filenames


class TestGetPdfEndpoint:
    """GET /pdf/{doc_id}"""

    def test_get_existing_returns_full_detail(self):
        """Getting an existing PDF returns full detail with text."""
        doc = _make_document(text_content="Full document text here")
        mock_svc = MagicMock()
        mock_svc.find_by_id.return_value = doc

        client = TestClient(create_test_app(mock_svc))
        resp = client.get("/pdf/507f1f77bcf86cd799439011")

        assert resp.status_code == 200
        body = resp.json()
        assert body["text_content"] == "Full document text here"
        assert body["filename"] == "document.pdf"

    def test_get_not_found_returns_404(self):
        """Getting a non-existent PDF returns 404."""
        mock_svc = MagicMock()
        mock_svc.find_by_id.return_value = None

        client = TestClient(create_test_app(mock_svc))
        resp = client.get("/pdf/nonexistent-id")

        assert resp.status_code == 404


class TestDeletePdfEndpoint:
    """DELETE /pdf/{doc_id}"""

    def test_delete_existing_returns_204(self):
        """Deleting an existing PDF returns 204 No Content."""
        mock_svc = MagicMock()
        mock_svc.delete_by_id.return_value = True

        client = TestClient(create_test_app(mock_svc))
        resp = client.delete("/pdf/507f1f77bcf86cd799439011")

        assert resp.status_code == 204

    def test_delete_not_found_returns_404(self):
        """Deleting a non-existent PDF returns 404."""
        mock_svc = MagicMock()
        mock_svc.delete_by_id.return_value = False

        client = TestClient(create_test_app(mock_svc))
        resp = client.delete("/pdf/nonexistent")

        assert resp.status_code == 404


class TestExtractTextEndpoint:
    """POST /pdf/{file_id}/extract"""

    def test_extract_from_existing_returns_text(self):
        """Extracting text from existing PDF returns content."""
        doc = _make_document(text_content="Page 1 text Page 2 text")
        mock_svc = MagicMock()
        mock_svc.extract_text_from_pdf = AsyncMock(return_value=doc)

        client = TestClient(create_test_app(mock_svc))
        resp = client.post("/pdf/507f1f77bcf86cd799439011/extract")

        assert resp.status_code == 200
        body = resp.json()
        assert body["text"] == "Page 1 text Page 2 text"
        assert body["pages_extracted"] == 5

    def test_extract_not_found_returns_404(self):
        """Extracting from non-existent PDF returns 404."""
        mock_svc = MagicMock()
        mock_svc.extract_text_from_pdf = AsyncMock(
            side_effect=PDFNotFoundException("Not found")
        )

        client = TestClient(create_test_app(mock_svc))
        resp = client.post("/pdf/missing/extract")

        assert resp.status_code == 404
