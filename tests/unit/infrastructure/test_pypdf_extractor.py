"""Adaptador pypdf contra PDFs reales generados en memoria."""

import pytest

from app.domain.exceptions import PDFExtractionException
from app.infrastructure.pypdf_extractor import PypdfTextExtractor
from tests.support.pdf_builder import build_pdf

extract = PypdfTextExtractor().extract


def test_extracts_text_of_every_page():
    result = extract(build_pdf("Primera pagina", "Segunda pagina"))

    assert result.page_count == 2
    assert "Primera pagina" in result.text
    assert "Segunda pagina" in result.text


def test_pdf_without_text_returns_empty_text_and_page_count():
    result = extract(build_pdf("", ""))

    assert result.text == ""
    assert result.page_count == 2


def test_extracts_non_ascii_text():
    assert "Ñandú café" in extract(build_pdf("Ñandú café")).text


@pytest.mark.parametrize("content", [b"no es un pdf", b"%PDF-1.4 truncado"])
def test_unreadable_content_raises_domain_exception(content):
    with pytest.raises(PDFExtractionException):
        extract(content)
