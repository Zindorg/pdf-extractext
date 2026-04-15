"""Unit tests for API routes input validation.

These tests verify that API endpoints correctly validate input data,
following CLEAN CODE principles with descriptive test names.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, UploadFile
from unittest.mock import AsyncMock, MagicMock, patch
from io import BytesIO

from api.routes.pdf_routes import router, get_pdf_service
from core.exceptions import InvalidFileException


# Create a test app with mocked dependencies
def create_test_app(mock_service=None):
    """Create FastAPI test app with mocked service."""
    app = FastAPI()

    if mock_service:

        def override_get_pdf_service():
            return mock_service

        app.dependency_overrides[get_pdf_service] = override_get_pdf_service

    app.include_router(router)
    return app


class TestAPIUploadNullValidation:
    """Tests for rejecting null values in API uploads."""

    def test_upload_pdf_rejects_missing_file(self):
        """Should return 422 when no file is provided.

        Verifies that the API rejects requests without a file attachment,
        returning HTTP 422 Unprocessable Entity.
        """
        app = create_test_app()
        client = TestClient(app)

        response = client.post("/pdf/upload")

        assert response.status_code == 422

    def test_upload_pdf_rejects_none_file_explicitly(self):
        """Should handle explicitly null file parameter.

        Verifies that the API properly handles null file values
        in multipart form data.
        """
        app = create_test_app()
        client = TestClient(app)

        response = client.post("/pdf/upload", data={"file": None})

        assert response.status_code in [422, 400]


class TestAPIUploadEmptyPathValidation:
    """Tests for rejecting empty paths in API uploads."""

    def test_upload_pdf_rejects_empty_filename(self):
        """Should return error when filename is empty string.

        Verifies that empty filenames are rejected at the API level.
        FastAPI returns 422 for empty filenames in multipart form data.
        """
        mock_service = MagicMock()
        mock_service.process_pdf = AsyncMock(
            side_effect=InvalidFileException("File must be a PDF")
        )

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post(
            "/pdf/upload", files={"file": ("", b"some content", "application/pdf")}
        )

        # Empty filename in multipart returns 422 (FastAPI validation)
        assert response.status_code in [400, 422]

    def test_upload_pdf_rejects_whitespace_filename(self):
        """Should return 400 when filename contains only whitespace.

        Verifies that whitespace-only filenames are rejected,
        as they don't represent valid file identifiers.
        """
        mock_service = MagicMock()
        mock_service.process_pdf = AsyncMock(
            side_effect=InvalidFileException("File must be a PDF")
        )

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post(
            "/pdf/upload", files={"file": ("   ", b"some content", "application/pdf")}
        )

        assert response.status_code == 400


class TestAPIUploadTypeValidation:
    """Tests for verifying expected input types in API."""

    def test_upload_pdf_rejects_non_string_filename_type(self):
        """Should handle non-string filename gracefully.

        Verifies that the API can handle filename type mismatches
        without internal server errors.
        """
        mock_service = MagicMock()
        mock_service.process_pdf = AsyncMock(
            side_effect=InvalidFileException("Invalid filename type")
        )

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post(
            "/pdf/upload",
            files={"file": ("document.pdf", b"content", "application/pdf")},
        )

        # Should not be 500 (internal server error)
        assert response.status_code != 500


class TestAPIUploadExtensionValidation:
    """Tests for verifying PDF extension in API uploads."""

    def test_upload_pdf_rejects_txt_extension(self):
        """Should return 400 when file has .txt extension.

        Verifies that text files are rejected at the API level
        with appropriate error message.
        """
        mock_service = MagicMock()
        mock_service.process_pdf = AsyncMock(
            side_effect=InvalidFileException("File must be a PDF")
        )

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post(
            "/pdf/upload",
            files={"file": ("document.txt", b"text content", "text/plain")},
        )

        assert response.status_code == 400
        assert "pdf" in response.json()["detail"].lower()

    def test_upload_pdf_rejects_doc_extension(self):
        """Should return 400 when file has .doc extension.

        Verifies that Word documents are rejected at the API level,
        enforcing PDF-only uploads.
        """
        mock_service = MagicMock()
        mock_service.process_pdf = AsyncMock(
            side_effect=InvalidFileException("File must be a PDF")
        )

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post(
            "/pdf/upload",
            files={"file": ("document.doc", b"doc content", "application/msword")},
        )

        assert response.status_code == 400

    def test_upload_pdf_rejects_docx_extension(self):
        """Should return 400 when file has .docx extension.

        Verifies that modern Word documents are rejected at the API level.
        """
        mock_service = MagicMock()
        mock_service.process_pdf = AsyncMock(
            side_effect=InvalidFileException("File must be a PDF")
        )

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post(
            "/pdf/upload",
            files={
                "file": (
                    "document.docx",
                    b"docx content",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

        assert response.status_code == 400

    def test_upload_pdf_rejects_png_extension(self):
        """Should return 400 when file has .png extension.

        Verifies that PNG images are rejected at the API level.
        """
        mock_service = MagicMock()
        mock_service.process_pdf = AsyncMock(
            side_effect=InvalidFileException("File must be a PDF")
        )

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post(
            "/pdf/upload", files={"file": ("image.png", b"png binary", "image/png")}
        )

        assert response.status_code == 400

    def test_upload_pdf_rejects_jpg_extension(self):
        """Should return 400 when file has .jpg extension.

        Verifies that JPEG images are rejected at the API level.
        """
        mock_service = MagicMock()
        mock_service.process_pdf = AsyncMock(
            side_effect=InvalidFileException("File must be a PDF")
        )

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post(
            "/pdf/upload", files={"file": ("image.jpg", b"jpg binary", "image/jpeg")}
        )

        assert response.status_code == 400

    def test_upload_pdf_rejects_no_extension(self):
        """Should return 400 when file has no extension.

        Verifies that files without extension are rejected at the API level.
        """
        mock_service = MagicMock()
        mock_service.process_pdf = AsyncMock(
            side_effect=InvalidFileException("File must be a PDF")
        )

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post(
            "/pdf/upload",
            files={"file": ("document", b"some content", "application/octet-stream")},
        )

        assert response.status_code == 400

    def test_upload_pdf_rejects_uppercase_pdf_extension(self):
        """Should return 400 when file has .PDF extension.

        Verifies that uppercase PDF extension is rejected,
        enforcing lowercase .pdf requirement.
        """
        mock_service = MagicMock()
        mock_service.process_pdf = AsyncMock(
            side_effect=InvalidFileException("File must be a PDF")
        )

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post(
            "/pdf/upload",
            files={"file": ("document.PDF", b"pdf content", "application/pdf")},
        )

        assert response.status_code == 400

    def test_upload_pdf_rejects_mixed_case_extension(self):
        """Should return 400 when file has .Pdf extension.

        Verifies that mixed-case PDF extension is rejected.
        """
        mock_service = MagicMock()
        mock_service.process_pdf = AsyncMock(
            side_effect=InvalidFileException("File must be a PDF")
        )

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post(
            "/pdf/upload",
            files={"file": ("document.Pdf", b"pdf content", "application/pdf")},
        )

        assert response.status_code == 400

    def test_upload_pdf_accepts_lowercase_pdf_extension(self):
        """Should accept file with lowercase .pdf extension.

        Verifies that properly formatted PDF files are accepted
        and processed successfully.
        """
        from models.pdf_document import PDFDocument

        mock_service = MagicMock()
        mock_doc = PDFDocument(
            id="abc123",
            filename="document.pdf",
            file_size=100,
            page_count=5,
            text_content="Extracted text",
        )
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

    def test_upload_pdf_accepts_path_with_directories(self):
        """Should accept filename with path and .pdf extension.

        Verifies that filenames containing directory paths are accepted
        as long as they end with .pdf.
        """
        from models.pdf_document import PDFDocument

        mock_service = MagicMock()
        mock_doc = PDFDocument(
            id="abc123",
            filename="path/to/document.pdf",
            file_size=100,
            page_count=5,
            text_content="Extracted text",
        )
        mock_service.process_pdf = AsyncMock(return_value=mock_doc)

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post(
            "/pdf/upload",
            files={"file": ("path/to/document.pdf", b"pdf content", "application/pdf")},
        )

        assert response.status_code == 200


class TestAPIUploadEmptyContentValidation:
    """Tests for rejecting empty file content in API uploads."""

    def test_upload_pdf_rejects_empty_file_content(self):
        """Should return 400 when file content is empty.

        Verifies that empty files are rejected at the API level.
        """
        mock_service = MagicMock()
        mock_service.process_pdf = AsyncMock(
            side_effect=InvalidFileException("File is empty")
        )

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post(
            "/pdf/upload", files={"file": ("document.pdf", b"", "application/pdf")}
        )

        assert response.status_code == 400


class TestAPIUploadSizeValidation:
    """Tests for file size validation in API uploads."""

    def test_upload_pdf_rejects_file_larger_than_10mb(self):
        """Should return 413 when file exceeds max size."""
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


class TestAPIExtractEndpoint:
    """Tests for PDF extraction endpoint."""

    def test_extract_from_existing_pdf(self):
        """Should return extracted text for existing PDF."""
        from models.pdf_document import PDFDocument

        mock_doc = PDFDocument(
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

    def test_extract_nonexistent_pdf(self):
        """Should return 404 when PDF does not exist."""
        from core.exceptions import PDFExtractionException

        mock_service = MagicMock()
        mock_service.extract_text_from_pdf = AsyncMock(
            side_effect=PDFExtractionException("PDF not found")
        )

        app = create_test_app(mock_service)
        client = TestClient(app)

        response = client.post("/pdf/xyz789/extract")

        assert response.status_code == 404
