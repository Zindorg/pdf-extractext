"""Tests para generate_checksum - determinismo."""

from app.services.pdf_utils import generate_checksum


class TestGenerateChecksumDeterministic:
    """Mismo contenido produce mismo checksum."""

    def test_same_content_same_checksum(self):
        content = b"deterministic content"
        c1 = generate_checksum(content)
        c2 = generate_checksum(content)
        assert c1 == c2
