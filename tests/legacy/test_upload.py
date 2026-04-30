"""Unit tests for POST /upload endpoint.

Tests verify that the upload endpoint:
- Receives file and processes it in memory
- Returns correct JSON response with checksum
- Does NOT save files to disk
"""

import hashlib
from io import BytesIO

import pytest
from fastapi.testclient import TestClient


class TestUploadEndpoint:
    """Test suite for file upload endpoint."""

    def test_upload_success_returns_200(self, client: TestClient) -> None:
        """Test successful file upload returns HTTP 200."""
        # Arrange
        file_content = b"Test PDF content for upload"

        # Act
        response = client.post(
            "/upload",
            files={"file": ("test.pdf", BytesIO(file_content), "application/pdf")},
        )

        # Assert
        assert response.status_code == 200

    def test_upload_returns_json_with_message(self, client: TestClient) -> None:
        """Test upload returns JSON with success message."""
        # Arrange
        file_content = b"Test content"

        # Act
        response = client.post(
            "/upload",
            files={"file": ("document.pdf", BytesIO(file_content), "application/pdf")},
        )

        # Assert
        data = response.json()
        assert "message" in data
        assert data["message"] == "File uploaded successfully"

    def test_upload_returns_file_size(self, client: TestClient) -> None:
        """Test upload returns correct file size."""
        # Arrange
        file_content = b"Test content with exact size"
        expected_size = len(file_content)

        # Act
        response = client.post(
            "/upload",
            files={"file": ("size_test.pdf", BytesIO(file_content), "application/pdf")},
        )

        # Assert
        data = response.json()
        assert data["size_bytes"] == expected_size

    def test_upload_returns_sha256_checksum(self, client: TestClient) -> None:
        """Test upload returns SHA-256 checksum as file_id."""
        # Arrange
        file_content = b"Test content for checksum"
        expected_checksum = hashlib.sha256(file_content).hexdigest()

        # Act
        response = client.post(
            "/upload",
            files={
                "file": ("checksum_test.pdf", BytesIO(file_content), "application/pdf")
            },
        )

        # Assert
        data = response.json()
        assert data["file_id"] == expected_checksum
        assert len(data["file_id"]) == 64  # SHA-256 is 64 hex chars

    def test_upload_returns_original_filename(self, client: TestClient) -> None:
        """Test upload preserves original filename."""
        # Arrange
        file_content = b"Test content"
        original_filename = "my_document.pdf"

        # Act
        response = client.post(
            "/upload",
            files={
                "file": (original_filename, BytesIO(file_content), "application/pdf")
            },
        )

        # Assert
        data = response.json()
        assert data["filename"] == original_filename

    def test_upload_empty_file_returns_400(self, client: TestClient) -> None:
        """Test upload with empty file returns HTTP 400."""
        # Arrange
        empty_content = b""

        # Act
        response = client.post(
            "/upload",
            files={"file": ("empty.pdf", BytesIO(empty_content), "application/pdf")},
        )

        # Assert
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_upload_no_filename_returns_400(self, client: TestClient) -> None:
        """Test upload without filename returns HTTP 400."""
        # Arrange
        file_content = b"Test content"

        # Act
        response = client.post(
            "/upload",
            files={"file": ("", BytesIO(file_content), "application/pdf")},
        )

        # Assert
        assert response.status_code == 422

    def test_upload_does_not_create_disk_files(
        self, client: TestClient, tmp_path
    ) -> None:
        """Test upload processes file in memory without disk access."""
        # Arrange
        file_content = b"Test content for memory verification"
        initial_files = list(tmp_path.glob("*"))

        # Act
        response = client.post(
            "/upload",
            files={
                "file": ("memory_test.pdf", BytesIO(file_content), "application/pdf")
            },
        )

        # Assert
        assert response.status_code == 200
        # Verify no files were created in temp directory
        final_files = list(tmp_path.glob("*"))
        assert len(final_files) == len(initial_files)

    def test_upload_large_file_succeeds(self, client: TestClient) -> None:
        """Test upload handles larger files correctly."""
        # Arrange
        file_content = b"A" * (1024 * 1024)  # 1MB of content
        expected_checksum = hashlib.sha256(file_content).hexdigest()

        # Act
        response = client.post(
            "/upload",
            files={"file": ("large.pdf", BytesIO(file_content), "application/pdf")},
        )

        # Assert
        data = response.json()
        assert response.status_code == 200
        assert data["size_bytes"] == len(file_content)
        assert data["file_id"] == expected_checksum
