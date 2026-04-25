"""Custom exceptions for the application."""


class PDFExtractextException(Exception):
    """Base exception for the application."""


class PDFNotFoundException(PDFExtractextException):
    """PDF not found."""


class PDFExtractionException(PDFExtractextException):
    """Error extracting text from PDF."""


class InvalidFileException(PDFExtractextException):
    """Invalid file."""
