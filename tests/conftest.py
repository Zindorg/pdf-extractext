"""Fixtures compartidas por toda la suite."""

import pytest

from tests.support.fakes import FakeTextExtractor, InMemoryPDFRepository


@pytest.fixture
def repository():
    """Repositorio en memoria, vacío en cada test."""
    return InMemoryPDFRepository()


@pytest.fixture
def extractor():
    return FakeTextExtractor()
