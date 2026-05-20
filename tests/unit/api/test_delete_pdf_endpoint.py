"""Tests para DELETE /pdfs/{doc_id}."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from tests.unit.api.utils import _create_test_app

class TestDelete:
    """Eliminar PDF existente retorna 204."""

    def test_returns_204(self):
        mock_svc = MagicMock()
        mock_svc.delete_by_id.return_value = True

        client = TestClient(_create_test_app(mock_svc))
        resp = client.delete("/pdfs/507f1f77bcf86cd799439011")

        assert resp.status_code == 204

    """Eliminar PDF inexistente retorna 404."""

    def test_returns_404(self):
        mock_svc = MagicMock()
        mock_svc.delete_by_id.return_value = False

        client = TestClient(_create_test_app(mock_svc))
        resp = client.delete("/pdfs/nonexistent")

        assert resp.status_code == 404
