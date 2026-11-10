"""Contrato HTTP de la API, de punta a punta.

Se ejercita el cableado real (rutas → casos de uso → extracción con pypdf)
y solo se reemplaza la persistencia por un repositorio en memoria. Estos
tests usan únicamente la interfaz pública (HTTP), así que sobreviven a
cualquier refactor interno de las capas.
"""

import hashlib
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pymongo.errors import AutoReconnect

from app.config.settings import settings
from app.dependencies import get_pdf_repository
from app.infrastructure.mongo_pdf_repository import MongoPDFRepository
from app.main import create_application
from tests.support.pdf_builder import build_pdf
from tests.unit.factories import make_pdf_document

URL = "/api/v1/pdfs"
UNKNOWN_ID = "507f1f77bcf86cd799439011"


@pytest.fixture
def client(repository):
    app = create_application()
    app.dependency_overrides[get_pdf_repository] = lambda: repository
    return TestClient(app)  # sin `with`: no corre el lifespan ni conecta a Mongo


def upload(client, content: bytes, filename: str = "informe.pdf"):
    return client.post(URL, files={"file": (filename, content, "application/pdf")})


def upload_id(client, text: str, filename: str = "informe.pdf") -> str:
    return upload(client, build_pdf(text), filename).json()["id"]


class TestUpload:
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
        assert set(body) == {"id", "filename", "page_count", "file_size", "checksum", "text_preview"}

    def test_persists_document_with_full_text(self, client, repository):
        doc_id = upload_id(client, "Contenido persistido")

        assert "Contenido persistido" in repository.find_by_id(doc_id).text_content

    def test_preview_is_truncated_to_500_chars(self, client):
        resp = upload(client, build_pdf(*(c * 90 for c in "xyzwvu")))

        assert resp.status_code == 200
        assert len(resp.json()["text_preview"]) == 500

    def test_duplicate_content_returns_409_problem_detail(self, client):
        content = build_pdf("Documento repetido")
        upload(client, content, "original.pdf")

        resp = upload(client, content, "copia.pdf")

        assert resp.status_code == 409
        assert resp.json()["title"] == "Conflict"
        assert resp.json()["status"] == 409

    def test_pdf_without_text_returns_422(self, client, repository):
        assert upload(client, build_pdf("")).status_code == 422
        assert repository.find_all() == []

    def test_corrupt_pdf_returns_422(self, client):
        assert upload(client, b"esto no es un pdf").status_code == 422

    def test_empty_file_returns_422(self, client):
        assert upload(client, b"").status_code == 422

    def test_non_pdf_extension_returns_422(self, client):
        assert upload(client, build_pdf("texto"), "notas.txt").status_code == 422

    def test_missing_file_returns_422_problem_detail(self, client):
        resp = client.post(URL)

        assert resp.status_code == 422
        assert resp.json()["title"] == "Unprocessable Entity"

    def test_file_larger_than_max_size_returns_422(self, client, repository, monkeypatch):
        content = build_pdf("Archivo grande")
        monkeypatch.setattr(settings, "max_file_size", len(content) - 1)

        resp = upload(client, content)

        assert resp.status_code == 422
        assert "too large" in resp.json()["detail"].lower()
        assert repository.find_all() == []


class TestList:
    def test_empty(self, client):
        assert client.get(URL).json() == {"documents": [], "total": 0}

    def test_returns_metadata_newest_first(self, client):
        first = upload_id(client, "Primero", "a.pdf")
        second = upload_id(client, "Segundo", "b.pdf")

        body = client.get(URL).json()

        assert body["total"] == 2
        assert [d["id"] for d in body["documents"]] == [second, first]
        assert set(body["documents"][0]) == {
            "id", "filename", "page_count", "file_size", "checksum", "created_at", "updated_at",
        }


class TestGetText:
    def test_returns_full_text(self, client):
        doc_id = upload_id(client, "Texto completo")

        body = client.get(f"{URL}/{doc_id}/text").json()

        assert body["id"] == doc_id
        assert body["filename"] == "informe.pdf"
        assert "Texto completo" in body["text"]
        assert body["page_count"] == 1
        assert set(body) == {"id", "filename", "text", "page_count"}

    def test_unknown_id_returns_404_problem_detail(self, client):
        resp = client.get(f"{URL}/{UNKNOWN_ID}/text")

        assert resp.status_code == 404
        assert resp.json()["title"] == "Not Found"


class TestDownload:
    def test_returns_text_as_txt_attachment(self, client):
        doc_id = upload_id(client, "Para descargar", "reporte.pdf")

        resp = client.get(f"{URL}/{doc_id}/download")

        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/plain")
        assert "Para descargar" in resp.text
        assert 'filename="reporte.txt"' in resp.headers["content-disposition"]

    @pytest.mark.parametrize(
        "pdf_name, expected",
        [
            ("INFORME.PDF", 'filename="INFORME.txt"'),
            ("mi.pdf.backup.pdf", 'filename="mi.pdf.backup.txt"'),
            ('año "final".pdf', 'filename="a_o _final_.txt"'),
        ],
    )
    def test_txt_name_is_derived_safely(self, client, repository, pdf_name, expected):
        # Se guarda directo en el repositorio: el cliente HTTP de test codifica
        # las comillas del nombre al subir, y aquí interesa el nombre exacto.
        doc_id = repository.create(make_pdf_document(filename=pdf_name)).id

        header = client.get(f"{URL}/{doc_id}/download").headers["content-disposition"]

        assert expected in header

    def test_non_ascii_name_is_kept_in_rfc6266_form(self, client, repository):
        doc_id = repository.create(make_pdf_document(filename='año "final".pdf')).id

        header = client.get(f"{URL}/{doc_id}/download").headers["content-disposition"]

        assert "filename*=UTF-8''a%C3%B1o%20%22final%22.txt" in header

    def test_unknown_id_returns_404(self, client):
        assert client.get(f"{URL}/{UNKNOWN_ID}/download").status_code == 404


class TestDelete:
    def test_deletes_document(self, client):
        doc_id = upload_id(client, "Para borrar")

        assert client.delete(f"{URL}/{doc_id}").status_code == 204
        assert client.get(f"{URL}/{doc_id}/text").status_code == 404
        assert client.get(URL).json()["total"] == 0

    def test_unknown_id_returns_404(self, client):
        assert client.delete(f"{URL}/{UNKNOWN_ID}").status_code == 404

    def test_same_content_can_be_uploaded_again_after_delete(self, client):
        content = build_pdf("Volver a subir")
        doc_id = upload(client, content).json()["id"]
        client.delete(f"{URL}/{doc_id}")

        assert upload(client, content).status_code == 200



class TestServerErrors:
    def test_database_failure_is_500_without_leaking_driver_details(self, client):
        database = MagicMock()
        database.__getitem__.return_value.find.side_effect = AutoReconnect(
            "mongo-internal:27017 connection refused"
        )
        client.app.dependency_overrides[get_pdf_repository] = lambda: MongoPDFRepository(database)

        resp = client.get(URL)

        assert resp.status_code == 500
        assert resp.json()["title"] == "Internal Server Error"
        assert "mongo-internal" not in resp.text
