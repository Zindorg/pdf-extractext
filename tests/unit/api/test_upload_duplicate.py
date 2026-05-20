"""Tests para POST /pdfs - upload duplicado."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from tests.unit.api.utils import _create_test_app, _make_document


class TestUploadDuplicatePdf:
    """Subir PDF duplicado retorna doc existente."""

    def test_returns_existing_with_flag_true(self):
        existing = _make_document()
        mock_svc = MagicMock()
        mock_svc.generate_checksum.return_value = "same_checksum"
        mock_svc.find_by_checksum.return_value = existing

        client = TestClient(_create_test_app(mock_svc))
        resp = client.post(
            "/pdfs",
            files={"file": ("doc.pdf", b"same content", "application/pdf")},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["is_duplicate"] is True
        assert body["id"] == existing.id
