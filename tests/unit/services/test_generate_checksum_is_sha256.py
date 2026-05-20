"""Tests para generate_checksum - formato SHA-256."""

from app.services.pdf_service import PDFService


class TestGenerateChecksumIsSha256:
    """Checksum es SHA-256 hex de 64 caracteres."""

    def test_is_sha256_hex(self):
        pdf_service = PDFService()
        checksum = pdf_service.generate_checksum(b"test")
        assert len(checksum) == 64
        int(checksum, 16)
