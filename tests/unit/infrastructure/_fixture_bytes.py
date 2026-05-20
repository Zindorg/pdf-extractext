from pathlib import Path

def _fixture_bytes(filename: str) -> bytes:
    """Carga un fixture PDF como bytes."""
    fixture_path = Path(__file__).parent.parent.parent / "fixtures" / filename
    return fixture_path.read_bytes()