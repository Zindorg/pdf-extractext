"""Pure utility functions for PDF processing.

These functions have no side effects and operate only on their inputs.
They can be tested in isolation without any dependencies.
"""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path

from app.exceptions import InvalidFileException

logger = logging.getLogger(__name__)


def generate_checksum(file_content: bytes) -> str:
    """Generate SHA-256 checksum from file content."""
    checksum = hashlib.sha256(file_content).hexdigest()
    logger.debug("Generated checksum: %s", checksum)
    return checksum


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe usage."""
    base = Path(filename).stem
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
    result = sanitized[:50] or "document"
    logger.debug("Sanitized filename: %s -> %s", filename, result)
    return result


def validate_filename(filename: str) -> None:
    """Validate filename format."""
    if not filename:
        logger.warning("Validation failed: empty filename")
        raise InvalidFileException("Filename cannot be empty")
    if not filename.strip():
        logger.warning("Validation failed: whitespace-only filename")
        raise InvalidFileException("Filename cannot be whitespace only")
    suffix = Path(filename).suffix.lower()
    if not suffix or suffix != ".pdf":
        logger.warning("Validation failed: non-PDF file: %s", filename)
        raise InvalidFileException("File must be a PDF")
    logger.debug("Filename validation passed: %s", filename)


def validate_content(file_content: bytes) -> None:
    """Validate file content is not empty."""
    if not file_content:
        logger.warning("Validation failed: empty file content")
        raise InvalidFileException("File is empty")
    logger.debug("Content validation passed (%d bytes)", len(file_content))
