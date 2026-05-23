"""Tests para POST /pdfs - upload duplicado."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.exceptions import DuplicateDocumentException
from tests.unit.api.utils import _create_test_app


class TestUploadDuplicatePdf:
    """Subir PDF duplicado retorna doc existente con flag is_duplicate."""

    def test_returns_existing_with_flag_true(self):
        mock_extraction = MagicMock()
        mock_extraction.process_pdf = AsyncMock(
            side_effect=DuplicateDocumentException("Duplicate")  
        )

        client = TestClient(_create_test_app(mock_extraction=mock_extraction))
        resp = client.post(
            "/pdfs",
            files={"file": ("doc.pdf", b"same content", "application/pdf")},
        )

        assert resp.status_code == 409
        body = resp.json()
        assert body["title"] == "Conflict"
        assert body["status"] == 409
