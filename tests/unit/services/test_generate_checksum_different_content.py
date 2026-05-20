"""Tests para generate_checksum - contenido diferente."""

from app.services.pdf_service import PDFService


class TestGenerateChecksumDifferentContent:
    """Diferente contenido produce diferente checksum."""

    def test_different_content(self):
        pdf_service = PDFService()
        c1 = pdf_service.generate_checksum(b"content_a")
        c2 = pdf_service.generate_checksum(b"content_b")
        assert c1 != c2
