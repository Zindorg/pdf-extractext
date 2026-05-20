"""Tests para generate_checksum - determinismo."""

from app.services.pdf_service import PDFService


class TestGenerateChecksumDeterministic:
    """Mismo contenido produce mismo checksum."""

    def test_same_content_same_checksum(self):
        pdf_service = PDFService()
        content = b"deterministic content"
        c1 = pdf_service.generate_checksum(content)
        c2 = pdf_service.generate_checksum(content)
        assert c1 == c2
