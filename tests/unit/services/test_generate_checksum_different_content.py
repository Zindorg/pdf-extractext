"""Tests para generate_checksum - contenido diferente."""

from app.services.pdf_utils import generate_checksum


class TestGenerateChecksumDifferentContent:
    """Diferente contenido produce diferente checksum."""

    def test_different_content(self):
        c1 = generate_checksum(b"content_a")
        c2 = generate_checksum(b"content_b")
        assert c1 != c2
