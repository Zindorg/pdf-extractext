"""Tests para la interfaz de repositorio PDF."""

import inspect

import pytest

from app.repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface


class TestRepositoryInterfaceMethods:
    """Tests que verifican los métodos CRUD requeridos en la interfaz."""

    @pytest.mark.parametrize(
        "method_name",
        ["create", "find_by_id", "find_all", "delete_by_id", "find_by_checksum"],
    )
    def test_interface_has_required_methods(self, method_name):
        assert hasattr(PDFRepositoryInterface, method_name)

    def test_create_accepts_pdf_document(self):
        sig = inspect.signature(PDFRepositoryInterface.create)
        assert "document" in sig.parameters

    def test_find_by_checksum_accepts_string(self):
        sig = inspect.signature(PDFRepositoryInterface.find_by_checksum)
        assert "checksum" in sig.parameters

    def test_find_by_id_accepts_string(self):
        sig = inspect.signature(PDFRepositoryInterface.find_by_id)
        assert "doc_id" in sig.parameters
