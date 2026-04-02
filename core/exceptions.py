"""Custom exceptions for the application."""


class PDFExtractextException(Exception):
    """Base exception for the application."""

    pass


class PDFNotFoundException(PDFExtractextException):
    """PDF not found."""

    pass


class PDFExtractionException(PDFExtractextException):
    """Error extracting text from PDF."""

    pass


class InvalidFileException(PDFExtractextException):
    """Invalid file."""

    pass
