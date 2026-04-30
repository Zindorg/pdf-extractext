"""Factory for creating repository instances with proper dependency injection."""

from typing import Optional

from app.infrastructure.database_connection import get_database
from app.repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface
from app.repositories.mongo_pdf_repository import MongoPDFRepository


class RepositoryFactory:
    """Factory for creating configured repository instances.

    Esta clase centraliza la creación de instancias de repositorios,
    implementando el patrón Factory con inicialización lazy (perezosa).

    Garantiza que:
    - Solo existe una instancia de cada repositorio (singleton de facto)
    - La conexión a MongoDB se establece solo cuando se necesita
    - Los tests pueden hacer reset del estado fácilmente

    Example:
        >>> from repositories.repository_factory import RepositoryFactory
        >>> repo = RepositoryFactory.get_pdf_repository()
        >>> doc = repo.find_by_id("507f1f77bcf86cd799439011")

        >>> # Para tests:
        >>> RepositoryFactory.reset()
    """

    _pdf_repository: Optional[PDFRepositoryInterface] = None

    @classmethod
    def get_pdf_repository(cls) -> PDFRepositoryInterface:
        """Get or create PDF repository singleton.

        Retorna una instancia de MongoPDFRepository configurada
        con la conexión a MongoDB. Si ya existe una instancia,
        la retorna (patrón singleton).

        Returns:
            Configured MongoPDFRepository instance.

        Example:
            >>> repo = RepositoryFactory.get_pdf_repository()
            >>> doc = repo.find_by_checksum("abc123")
        """
        if cls._pdf_repository is None:
            db = get_database()
            cls._pdf_repository = MongoPDFRepository(database=db)
        return cls._pdf_repository

    @classmethod
    def reset(cls) -> None:
        """Reset factory state.

        Útil para tests de integración donde se necesita
        una instancia fresca entre tests.

        Example:
            >>> def setup_test():
            ...     RepositoryFactory.reset()
            ...     repo = RepositoryFactory.get_pdf_repository()
        """
        cls._pdf_repository = None

    @classmethod
    def set_repository(cls, repository: PDFRepositoryInterface) -> None:
        """Set a custom repository instance.

        Útil para inyectar mocks en tests unitarios.

        Args:
            repository: Custom repository instance to use.

        Example:
            >>> mock_repo = Mock(spec=PDFRepositoryInterface)
            >>> RepositoryFactory.set_repository(mock_repo)
        """
        cls._pdf_repository = repository
