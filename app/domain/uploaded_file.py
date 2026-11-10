"""Value object for a file received in an upload."""

import hashlib
from dataclasses import dataclass
from pathlib import PurePath

from app.domain.exceptions import InvalidFileException


@dataclass(frozen=True)
class UploadedFile:
    """A non-empty file whose name has a .pdf extension.

    Creating one validates those invariants, so any UploadedFile that
    exists is known to be acceptable as a PDF upload.
    """

    filename: str
    content: bytes

    def __post_init__(self) -> None:
        if not self.filename or not self.filename.strip():
            raise InvalidFileException("Filename cannot be empty")
        if PurePath(self.filename).suffix.lower() != ".pdf":
            raise InvalidFileException("File must be a PDF")
        if not self.content:
            raise InvalidFileException("File is empty")

    @property
    def size(self) -> int:
        return len(self.content)

    @property
    def checksum(self) -> str:
        """SHA-256 of the content: two uploads are the same document iff it matches."""
        return hashlib.sha256(self.content).hexdigest()

    def ensure_not_larger_than(self, max_size: int) -> None:
        if self.size > max_size:
            raise InvalidFileException(f"File too large: maximum size is {max_size} bytes")
