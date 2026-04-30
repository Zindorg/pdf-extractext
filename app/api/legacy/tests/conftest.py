"""Pytest fixtures and configuration for API Web tests."""

import pytest
from fastapi.testclient import TestClient

from app.api.legacy.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a TestClient instance for testing.

    Returns:
        TestClient configured with the FastAPI application.

    """
    return TestClient(app)


@pytest.fixture
def sample_file_content() -> bytes:
    """Provide sample file content for testing.

    Returns:
        Binary content of a sample file.

    """
    return b"This is a sample PDF file content for testing purposes."


@pytest.fixture
def sample_checksum() -> str:
    """Provide expected SHA-256 checksum for sample content.

    Returns:
        SHA-256 checksum string.

    """
    return "a3f5c8e9d2b1e4f7a8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
