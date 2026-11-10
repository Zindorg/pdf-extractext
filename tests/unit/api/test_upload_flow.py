"""Comportamiento de la subida de PDFs, de punta a punta por HTTP.

Se ejercita el cableado real (rutas → casos de uso → extracción con pypdf)
y solo se reemplaza la persistencia por un repositorio en memoria. Estos
tests usan únicamente la interfaz pública (HTTP), así que sobreviven a
cualquier refactor interno de las capas.
"""

import hashlib

import pytest
from fastapi.testclient import TestClient

from app.config.settings import settings
from app.dependencies import get_pdf_repository
from app.main import create_application
from tests.support.fakes import InMemoryPDFRepository
from tests.support.pdf_builder import build_pdf

URL = "/api/v1/pdfs"


@pytest.fixture
def repository():
    return InMemoryPDFRepository()


@pytest.fixture
def client(repository):
    app = create_application()
    app.dependency_overrides[get_pdf_repository] = lambda: repository
    return TestClient(app)  # sin `with`: no corre el lifespan ni conecta a Mongo


def upload(client, content: bytes, filename: str = "informe.pdf"):
    return client.post(URL, files={"file": (filename, content, "application/pdf")})


class TestUploadValidPdf:
    def test_returns_metadata_and_text_preview(self, client):
        content = build_pdf("Hola mundo", "Segunda pagina")

        resp = upload(client, content)

        assert resp.status_code == 200
        body = resp.json()
        assert body["filename"] == "informe.pdf"
        assert body["page_count"] == 2
        assert body["file_size"] == len(content)
        assert body["checksum"] == hashlib.sha256(content).hexdigest()
        assert "Hola mundo" in body["text_preview"]

    def test_persists_document_with_full_text(self, client, repository):
        resp = upload(client, build_pdf("Contenido persistido"))

        stored = repository.find_by_id(resp.json()["id"])
        assert stored is not None
        assert "Contenido persistido" in stored.text_content

    def test_preview_is_truncated_to_500_chars(self, client):
        resp = upload(client, build_pdf("x" * 90, "y" * 90, "z" * 90, "w" * 90, "v" * 90, "u" * 90))

        assert resp.status_code == 200
        assert len(resp.json()["text_preview"]) == 500


class TestUploadRejections:
    def test_duplicate_content_returns_409(self, client):
        content = build_pdf("Documento repetido")
        upload(client, content, "original.pdf")

        resp = upload(client, content, "copia.pdf")

        assert resp.status_code == 409
        assert resp.json()["title"] == "Conflict"

    def test_pdf_without_text_returns_422(self, client, repository):
        resp = upload(client, build_pdf(""))

        assert resp.status_code == 422
        assert repository.find_all() == []

    def test_corrupt_pdf_returns_422(self, client):
        resp = upload(client, b"esto no es un pdf")

        assert resp.status_code == 422

    def test_empty_file_returns_422(self, client):
        assert upload(client, b"").status_code == 422

    def test_non_pdf_extension_returns_422(self, client):
        assert upload(client, build_pdf("texto"), "notas.txt").status_code == 422

    def test_file_larger_than_max_size_returns_422(self, client, repository, monkeypatch):
        content = build_pdf("Archivo grande")
        monkeypatch.setattr(settings, "max_file_size", len(content) - 1)

        resp = upload(client, content)

        assert resp.status_code == 422
        assert "too large" in resp.json()["detail"].lower()
        assert repository.find_all() == []


class TestDocumentLifecycle:
    """Subir → listar → leer texto → descargar → borrar, por la API."""

    def test_full_lifecycle(self, client):
        doc_id = upload(client, build_pdf("Ciclo de vida"), "ciclo.pdf").json()["id"]

        listing = client.get(URL).json()
        assert listing["total"] == 1
        assert listing["documents"][0]["id"] == doc_id

        text = client.get(f"{URL}/{doc_id}/text").json()
        assert "Ciclo de vida" in text["text"]

        download = client.get(f"{URL}/{doc_id}/download")
        assert download.status_code == 200
        assert "Ciclo de vida" in download.text
        assert 'filename="ciclo.txt"' in download.headers["content-disposition"]

        assert client.delete(f"{URL}/{doc_id}").status_code == 204
        assert client.get(f"{URL}/{doc_id}/text").status_code == 404
        assert client.get(URL).json()["total"] == 0

    def test_unknown_id_returns_404_everywhere(self, client):
        unknown = "507f1f77bcf86cd799439011"
        assert client.get(f"{URL}/{unknown}/text").status_code == 404
        assert client.get(f"{URL}/{unknown}/download").status_code == 404
        assert client.delete(f"{URL}/{unknown}").status_code == 404