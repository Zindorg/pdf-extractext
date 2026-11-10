"""Domain errors.

They describe *what* went wrong in business terms. How each one is shown
to an HTTP client (status code, title) is decided by the API layer in
`app/api/exception_handlers.py`, not here.
"""


class PDFExtractextException(Exception):
    """Base class for every error raised by the application."""


class InvalidFileException(PDFExtractextException):
    """The uploaded file breaks an upload rule (name, emptiness, size)."""


class PDFExtractionException(PDFExtractextException):
    """The file is not a readable PDF or contains no text."""


class DuplicateDocumentException(PDFExtractextException):
    """A document with the same content (checksum) already exists."""

    def __init__(self, message: str, existing_id: str | None = None):
        super().__init__(message)
        self.existing_id = existing_id


class PDFNotFoundException(PDFExtractextException):
    """No document exists with the requested id."""


class RepositoryException(PDFExtractextException):
    """The storage failed while performing an operation."""
