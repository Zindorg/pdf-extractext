"""Tests para el caso de uso DeletePDF."""

from unittest.mock import MagicMock

from app.use_cases.delete_pdf import DeletePDF


class TestDeletePdf:
    """Eliminar PDF existente."""

    def test_returns_true(self):
        mock_commands = MagicMock()
        mock_commands.delete_by_id.return_value = True

        use_case = DeletePDF(mock_commands)
        result = use_case.execute("507f1f77bcf86cd799439011")

        assert result is True
    
    """Eliminar PDF inexistente."""

    def test_returns_false(self):
        mock_commands = MagicMock()
        mock_commands.delete_by_id.return_value = False

        use_case = DeletePDF(mock_commands)
        result = use_case.execute("nonexistent")

        assert result is False
