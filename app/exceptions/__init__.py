"""Custom exceptions for the application."""


class PDFExtractextException(Exception):
    """Base exception for the application."""

    def __init__(self, title: str = None, detail: str = None, status: int = 500):
        super().__init__(detail or title)
        self.title = title or "Internal Server Error"
        self.status = status


class PDFNotFoundException(PDFExtractextException):
    """PDF not found."""

    def __init__(self, detail: str = "PDF not found"):
        super().__init__(title="Not Found", detail=detail, status=404)


class PDFExtractionException(PDFExtractextException):
    """Error extracting text from PDF."""

    def __init__(self, detail: str = "Error extracting text from PDF"):
        super().__init__(title="Unprocessable Entity", detail=detail, status=422)


class InvalidFileException(PDFExtractextException):
    """Invalid file."""

    def __init__(self, detail: str = "Invalid file"):
        super().__init__(title="Unprocessable Entity", detail=detail, status=422)


class DuplicateDocumentException(PDFExtractextException):
    """PDF with same checksum already exists."""

    def __init__(
        self, detail: str = "Document already exists", existing_id: str = None
    ):
        super().__init__(title="Conflict", detail=detail, status=409)
        self.existing_id = existing_id


class DatabaseConnectionException(PDFExtractextException):
    """Failed to connect to database."""

    def __init__(self, detail: str = "Database connection failed"):
        super().__init__(title="Internal Server Error", detail=detail, status=500)


class RepositoryException(PDFExtractextException):
    """Repository operation failed."""

    def __init__(self, detail: str = "Repository operation failed"):
        super().__init__(title="Internal Server Error", detail=detail, status=500)
