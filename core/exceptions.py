"""Custom exceptions for the application."""


class PDFExtractextException(Exception):
    """Base exception for the application."""


class PDFNotFoundException(PDFExtractextException):
    """PDF not found."""


class PDFExtractionException(PDFExtractextException):
    """Error extracting text from PDF."""


class InvalidFileException(PDFExtractextException):
    """Invalid file."""


class DuplicateDocumentException(PDFExtractextException):
    """PDF with same checksum already exists."""

    def __init__(self, message: str, existing_id: str = None):
        super().__init__(message)
        self.existing_id = existing_id


class DatabaseConnectionException(PDFExtractextException):
    """Failed to connect to database."""


class RepositoryException(PDFExtractextException):
    """Repository operation failed."""
