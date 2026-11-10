"""Contrato de PDFRepository: toda implementación debe pasar estos tests.

Reemplaza a los tests de forma (inspect.signature) y a los mocks de la
colección: se verifica comportamiento a través de la interfaz pública,
y de paso se garantiza que el fake en memoria es fiel a MongoDB.
"""

from dataclasses import asdict
from datetime import datetime, timedelta

import pytest

from app.exceptions import DuplicateDocumentException
from tests.unit.factories import make_pdf_document

VALID_UNKNOWN_ID = "507f1f77bcf86cd799439011"


class TestCreate:
    def test_assigns_id_and_round_trips_all_fields(self, repo):
        original = make_pdf_document(checksum="c1", filename="a.pdf", text_content="hola")

        created = repo.create(original)
        found = repo.find_by_id(created.id)

        assert created.id
        assert _without_timestamps(found) == _without_timestamps(created)

    def test_timestamps_are_kept_with_millisecond_precision(self, repo):
        """BSON guarda fechas con precisión de milisegundos."""
        created = repo.create(make_pdf_document())
        found = repo.find_by_id(created.id)

        assert abs(found.created_at - created.created_at) < timedelta(milliseconds=1)
        assert abs(found.updated_at - created.updated_at) < timedelta(milliseconds=1)

    def test_duplicate_checksum_is_rejected(self, repo):
        repo.create(make_pdf_document(checksum="dup", filename="a.pdf"))

        with pytest.raises(DuplicateDocumentException):
            repo.create(make_pdf_document(checksum="dup", filename="b.pdf"))

        assert len(repo.find_all()) == 1


class TestFind:
    def test_find_by_checksum(self, repo):
        created = repo.create(make_pdf_document(checksum="buscado"))

        assert repo.find_by_checksum("buscado").id == created.id
        assert repo.find_by_checksum("otro") is None

    @pytest.mark.parametrize("doc_id", [VALID_UNKNOWN_ID, "no-es-un-object-id", ""])
    def test_find_by_id_returns_none_for_unknown_or_invalid_ids(self, repo, doc_id):
        assert repo.find_by_id(doc_id) is None

    def test_find_all_is_empty_initially(self, repo):
        assert repo.find_all() == []

    def test_find_all_returns_newest_first(self, repo):
        older = repo.create(make_pdf_document(checksum="old", created_at=datetime(2025, 1, 1)))
        newer = repo.create(make_pdf_document(checksum="new", created_at=datetime(2026, 1, 1)))

        assert [d.id for d in repo.find_all()] == [newer.id, older.id]


class TestDelete:
    def test_deleted_document_is_gone(self, repo):
        created = repo.create(make_pdf_document())

        assert repo.delete_by_id(created.id) is True
        assert repo.find_by_id(created.id) is None
        assert repo.find_all() == []

    def test_deleting_frees_the_checksum(self, repo):
        created = repo.create(make_pdf_document(checksum="reuse"))
        repo.delete_by_id(created.id)

        assert repo.create(make_pdf_document(checksum="reuse")).id

    @pytest.mark.parametrize("doc_id", [VALID_UNKNOWN_ID, "no-es-un-object-id"])
    def test_deleting_unknown_or_invalid_id_returns_false(self, repo, doc_id):
        assert repo.delete_by_id(doc_id) is False


def _without_timestamps(document) -> dict:
    data = asdict(document)
    del data["created_at"], data["updated_at"]
    return data
