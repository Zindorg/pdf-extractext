"""Centralized logging configuration for the application."""

import logging
import sys

_HANDLER_NAME = "pdf_extractext_console"


def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging for the application.

    Idempotent: calling it more than once (e.g. on every lifespan startup)
    does not duplicate log lines.

    Args:
        level: Minimum logging level to capture
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    handler = next((h for h in root_logger.handlers if h.get_name() == _HANDLER_NAME), None)
    if handler is None:
        handler = logging.StreamHandler(sys.stdout)
        handler.set_name(_HANDLER_NAME)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        root_logger.addHandler(handler)
    handler.setLevel(level)

    # Disable uvicorn access logs to avoid duplication
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)