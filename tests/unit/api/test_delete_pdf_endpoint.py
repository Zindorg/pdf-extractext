"""Tests para DELETE /pdfs/{doc_id}."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.exception_handlers import pdf_exception_handlers
from app.dependencies import get_delete_pdf_use_case
from app.routes.pdf_routes import router
from fastapi import FastAPI


def _create_delete_app(delete_mock):
    """Crea una aplicación de test mockeando el use case de borrado."""
    app = FastAPI()
    app.dependency_overrides[get_delete_pdf_use_case] = lambda: delete_mock
    for exc_class, handler in pdf_exception_handlers.items():
        app.add_exception_handler(exc_class, handler)
    app.include_router(router)
    return app


class TestDelete:
    """Eliminar PDF existente retorna 204."""

    def test_returns_204(self):
        mock_uc = MagicMock()
        mock_uc.execute.return_value = True

        client = TestClient(_create_delete_app(mock_uc))
        resp = client.delete("/pdfs/507f1f77bcf86cd799439011")

        assert resp.status_code == 204

    def test_returns_404(self):
        mock_uc = MagicMock()
        mock_uc.execute.return_value = False

        client = TestClient(_create_delete_app(mock_uc))
        resp = client.delete("/pdfs/nonexistent")

        assert resp.status_code == 404
        body = resp.json()
        assert body["title"] == "Not Found"
        assert body["status"] == 404
