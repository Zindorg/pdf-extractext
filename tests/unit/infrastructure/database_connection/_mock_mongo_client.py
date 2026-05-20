from unittest.mock import MagicMock, Mock
def _mock_mongo_client(mock_client_cls):
    mock_instance = MagicMock()
    mock_instance.admin.command.return_value = {"ok": 1}
    mock_db = MagicMock()
    mock_instance.__getitem__ = Mock(return_value=mock_db)
    mock_client_cls.return_value = mock_instance
    return mock_instance, mock_db