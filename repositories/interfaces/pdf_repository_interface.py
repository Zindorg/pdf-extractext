"""Interface for PDF repository (Dependency Inversion Principle)."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class PDFRepositoryInterface(ABC):
    """Abstract interface for PDF repository."""

    @abstractmethod
    async def save(self, file_content: bytes, filename: str) -> Path:
        """
        Save PDF file and return its path.

        Args:
            file_content: Binary content of the PDF
            filename: Original filename

        Returns:
            Path where the file was saved
        """
        pass

    @abstractmethod
    async def get(self, file_id: str) -> Optional[Path]:
        """
        Get file path by ID.

        Args:
            file_id: Unique identifier

        Returns:
            Path to file or None if not found
        """
        pass

    @abstractmethod
    async def delete(self, file_id: str) -> bool:
        """
        Delete file by ID.

        Args:
            file_id: Unique identifier

        Returns:
            True if deleted, False otherwise
        """
        pass
