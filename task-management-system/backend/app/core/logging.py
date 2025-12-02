"""Logging configuration using structlog."""
import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from app.core.config import settings


def configure_logging() -> None:
    """Configure structured logging for the application."""
    # Determine log level based on environment
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Shared processors for structlog
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # Development vs production formatting
    if settings.DEBUG:
        processors: list[Processor] = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> Any:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
