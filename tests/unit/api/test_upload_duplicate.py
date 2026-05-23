"""Tests para POST /pdfs - upload duplicado."""

from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from tests.unit.api.utils import _create_test_app, _make_document


class TestUploadDuplicatePdf:
    """Subir PDF duplicado retorna doc existente con flag is_duplicate."""

    def test_returns_existing_with_flag_true(self):
        existing = _make_document()
        mock_svc = MagicMock()
        mock_svc.process_upload = AsyncMock(return_value={
            "id": existing.id,
            "filename": existing.filename,
            "page_count": existing.page_count,
            "file_size": existing.file_size,
            "text_preview": existing.text_content[:500],
            "checksum": existing.checksum,
            "is_duplicate": True,
        })

        client = TestClient(_create_test_app(mock_svc))
        resp = client.post(
            "/pdfs",
            files={"file": ("doc.pdf", b"same content", "application/pdf")},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["is_duplicate"] is True
        assert body["id"] == existing.id
