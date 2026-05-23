"""Pure utility functions for PDF processing.

These functions have no side effects and operate only on their inputs.
They can be tested in isolation without any dependencies.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from app.exceptions import InvalidFileException


def generate_checksum(file_content: bytes) -> str:
    """Generate SHA-256 checksum from file content."""
    return hashlib.sha256(file_content).hexdigest()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe usage."""
    base = Path(filename).stem
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
    return sanitized[:50] or "document"


def validate_filename(filename: str) -> None:
    """Validate filename format."""
    if not filename:
        raise InvalidFileException("Filename cannot be empty")
    if not filename.strip():
        raise InvalidFileException("Filename cannot be whitespace only")
    suffix = Path(filename).suffix.lower()
    if not suffix or suffix != ".pdf":
        raise InvalidFileException("File must be a PDF")


def validate_content(file_content: bytes) -> None:
    """Validate file content is not empty."""
    if not file_content:
        raise InvalidFileException("File is empty")
