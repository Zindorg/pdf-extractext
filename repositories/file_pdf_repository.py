"""File system implementation of PDF repository (legacy, without CRUD interface)."""

import uuid
from pathlib import Path
from typing import Optional

from core.config import settings


class FilePDFRepository:
    """File system implementation for storing PDF files (not MongoDB compatible)."""

    def __init__(self) -> None:
        """Initialize repository with upload directory."""
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, file_content: bytes, filename: str) -> Path:
        """Save PDF file to disk."""
        file_id = str(uuid.uuid4())
        file_path = self.upload_dir / f"{file_id}_{filename}"

        with open(file_path, "wb") as f:
            f.write(file_content)

        return file_path

    async def get(self, file_id: str) -> Optional[Path]:
        """Get file path by ID."""
        for file in self.upload_dir.iterdir():
            if file.name.startswith(file_id):
                return file
        return None

    async def delete(self, file_id: str) -> bool:
        """Delete file by ID."""
        file_path = await self.get(file_id)
        if file_path and file_path.exists():
            file_path.unlink()
            return True
        return False
