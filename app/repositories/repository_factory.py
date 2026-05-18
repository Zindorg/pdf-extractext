"""Factory for creating repository instances with proper dependency injection."""

from typing import Optional

from app.infrastructure.database_connection import get_database
from app.repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface
from app.repositories.mongo_pdf_repository import MongoPDFRepository


class RepositoryFactory:
    """Factory for creating configured repository instances."""

    _pdf_repository: Optional[PDFRepositoryInterface] = None

    @classmethod
    def get_pdf_repository(cls) -> PDFRepositoryInterface:
        """Get or create PDF repository singleton."""
        if cls._pdf_repository is None:
            db = get_database()
            cls._pdf_repository = MongoPDFRepository(database=db)
        return cls._pdf_repository

    @classmethod
    def reset(cls) -> None:
        """Reset factory state."""
        cls._pdf_repository = None

    @classmethod
    def set_repository(cls, repository: PDFRepositoryInterface) -> None:
        """Set a custom repository instance."""
        cls._pdf_repository = repository
