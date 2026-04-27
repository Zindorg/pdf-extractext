"""Tests for PDF Repository Interface."""

import pytest
from typing import get_type_hints

from repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface


class TestRepositoryInterfaceMethods:
    """Tests that repository interface defines required CRUD methods."""

    def test_interface_has_create_method(self):
        """Should have create method."""
        assert hasattr(PDFRepositoryInterface, 'create')

    def test_interface_has_find_by_id_method(self):
        """Should have find_by_id method."""
        assert hasattr(PDFRepositoryInterface, 'find_by_id')

    def test_interface_has_find_all_method(self):
        """Should have find_all method."""
        assert hasattr(PDFRepositoryInterface, 'find_all')

    def test_interface_has_delete_by_id_method(self):
        """Should have delete_by_id method."""
        assert hasattr(PDFRepositoryInterface, 'delete_by_id')

    def test_interface_has_find_by_checksum_method(self):
        """Should have find_by_checksum method."""
        assert hasattr(PDFRepositoryInterface, 'find_by_checksum')

    def test_create_accepts_pdf_document(self):
        """Should accept PDFDocument in create."""
        from models.pdf_document import PDFDocument
        import inspect

        sig = inspect.signature(PDFRepositoryInterface.create)
        params = list(sig.parameters.keys())
        assert 'document' in params

    def test_find_by_checksum_accepts_string(self):
        """Should accept string checksum."""
        import inspect

        sig = inspect.signature(PDFRepositoryInterface.find_by_checksum)
        params = list(sig.parameters.keys())
        assert 'checksum' in params

    def test_find_by_id_accepts_string(self):
        """Should accept string id."""
        import inspect

        sig = inspect.signature(PDFRepositoryInterface.find_by_id)
        params = list(sig.parameters.keys())
        assert 'doc_id' in params
