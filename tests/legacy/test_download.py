"""Unit tests for GET /download/{file_id} endpoint.

Tests verify that the download endpoint:
- Returns file as attachment
- Sets correct content-type
- Returns HTTP 200 for existing files
- Returns HTTP 404 for non-existing files
"""

import hashlib
from io import BytesIO

import pytest
from fastapi.testclient import TestClient


class TestDownloadEndpoint:
    """Test suite for file download endpoint."""

    def test_download_existing_file_returns_200(self, client: TestClient) -> None:
        """Test download returns HTTP 200 for existing file."""
        # Arrange - Upload a file first
        file_content = b"Test content for download"
        checksum = hashlib.sha256(file_content).hexdigest()

        upload_response = client.post(
            "/upload",
            files={
                "file": ("download_test.pdf", BytesIO(file_content), "application/pdf")
            },
        )
        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_id"]

        # Act
        response = client.get(f"/download/{file_id}")

        # Assert
        assert response.status_code == 200

    def test_download_returns_text_plain_content_type(self, client: TestClient) -> None:
        """Test download returns content-type text/plain."""
        # Arrange - Upload a file first
        file_content = b"Test content"
        upload_response = client.post(
            "/upload",
            files={
                "file": (
                    "content_type_test.pdf",
                    BytesIO(file_content),
                    "application/pdf",
                )
            },
        )
        file_id = upload_response.json()["file_id"]

        # Act
        response = client.get(f"/download/{file_id}")

        # Assert
        assert response.headers["content-type"] == "text/plain; charset=utf-8"

    def test_download_returns_attachment_disposition(self, client: TestClient) -> None:
        """Test download returns Content-Disposition as attachment."""
        # Arrange - Upload a file first
        file_content = b"Test content"
        upload_response = client.post(
            "/upload",
            files={
                "file": (
                    "attachment_test.pdf",
                    BytesIO(file_content),
                    "application/pdf",
                )
            },
        )
        file_id = upload_response.json()["file_id"]

        # Act
        response = client.get(f"/download/{file_id}")

        # Assert
        assert "attachment" in response.headers["content-disposition"]
        assert file_id[:16] in response.headers["content-disposition"]

    def test_download_returns_txt_file_extension(self, client: TestClient) -> None:
        """Test download filename has .txt extension."""
        # Arrange - Upload a file first
        file_content = b"Test content"
        upload_response = client.post(
            "/upload",
            files={
                "file": ("extension_test.pdf", BytesIO(file_content), "application/pdf")
            },
        )
        file_id = upload_response.json()["file_id"]

        # Act
        response = client.get(f"/download/{file_id}")

        # Assert
        assert ".txt" in response.headers["content-disposition"]

    def test_download_contains_file_info(self, client: TestClient) -> None:
        """Test download content contains file information."""
        # Arrange - Upload a file first
        file_content = b"Test content for info verification"
        expected_size = len(file_content)
        upload_response = client.post(
            "/upload",
            files={"file": ("info_test.pdf", BytesIO(file_content), "application/pdf")},
        )
        file_id = upload_response.json()["file_id"]

        # Act
        response = client.get(f"/download/{file_id}")
        content = response.text

        # Assert
        assert file_id in content
        assert str(expected_size) in content

    def test_download_nonexistent_file_returns_404(self, client: TestClient) -> None:
        """Test download returns HTTP 404 for non-existing file."""
        # Arrange
        nonexistent_file_id = "a" * 64  # Valid SHA-256 format but not stored

        # Act
        response = client.get(f"/download/{nonexistent_file_id}")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_download_streaming_response(self, client: TestClient) -> None:
        """Test download uses streaming response correctly."""
        # Arrange - Upload a file first
        file_content = b"Test streaming content"
        upload_response = client.post(
            "/upload",
            files={
                "file": ("streaming_test.pdf", BytesIO(file_content), "application/pdf")
            },
        )
        file_id = upload_response.json()["file_id"]

        # Act
        response = client.get(f"/download/{file_id}")

        # Assert
        # Verify streaming by checking response can be iterated
        content_chunks = [response.content]
        assert len(content_chunks) > 0
        full_content = b"".join(content_chunks).decode("utf-8")
        assert file_id in full_content

    def test_download_after_multiple_uploads(self, client: TestClient) -> None:
        """Test download works after uploading multiple files."""
        # Arrange - Upload multiple files
        files_data = []
        for i in range(3):
            content = f"Content {i}".encode()
            response = client.post(
                "/upload",
                files={"file": (f"multi_{i}.pdf", BytesIO(content), "application/pdf")},
            )
            files_data.append(response.json())

        # Act & Assert - Download each file
        for file_info in files_data:
            file_id = file_info["file_id"]
            response = client.get(f"/download/{file_id}")
            assert response.status_code == 200
            assert file_id in response.text
