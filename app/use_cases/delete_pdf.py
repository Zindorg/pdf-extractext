"""Use case for deleting a PDF document."""

from app.services.pdf_commands import PDFCommands


class DeletePDF:
    """Handle PDF document deletion."""

    def __init__(self, commands: PDFCommands) -> None:
        """Initialize with commands service.

        Args:
            commands: Injected PDF commands service.
        """
        self._commands = commands

    def execute(self, doc_id: str) -> bool:
        """Permanently delete a PDF document by ID.

        Args:
            doc_id: Document ID.

        Returns:
            True if deleted, False otherwise.
        """
        return self._commands.delete_by_id(doc_id)
