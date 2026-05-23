"""Base class for PDF services with repository dependency."""

from app.repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface


class PDFCore:
    """Base class providing repository access to PDF service components."""

    def __init__(self, repository: PDFRepositoryInterface) -> None:
        """Initialize with repository.

        Args:
            repository: PDF repository for data access.
        """
        self._repository = repository
