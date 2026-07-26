"""Centralized logging configuration for the application."""
import logging
import sys

def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging for the application.
    
    Args:
        level: Minimum logging level to capture
    """
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Disable uvicorn access logs to avoid duplication
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

