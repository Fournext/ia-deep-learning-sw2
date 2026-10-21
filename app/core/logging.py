"""Configuración centralizada de logging estructurado para el microservicio."""

import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """Configura el formato y nivel de los logs del sistema."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    # Evitar handlers duplicados
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers = [handler]


logger = logging.getLogger("gym_ai")
