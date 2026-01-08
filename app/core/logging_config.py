"""Configuração centralizada de logging com saída em console e arquivo rotativo.

Parâmetros esperados:
    settings (Settings): Objeto de configuração com LOG_LEVEL e LOG_FILE definidos.

Uso:
    from app.core.logging_config import setup_logging, get_logger
    setup_logging(settings)
    logger = get_logger(__name__)
    logger.info("mensagem curta e autoexplicativa")
"""

from __future__ import annotations

import logging
import logging.config
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.core.config import settings

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(config_obj: settings.__class__ = settings) -> None:
    """Inicializa logging com console e arquivo rotativo.

    Parâmetros:
        config_obj (Settings): Objeto contendo LOG_LEVEL e LOG_FILE.

    Retorna:
        None
    """
    log_path = Path(config_obj.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": LOG_FORMAT,
                "datefmt": DATE_FORMAT,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": config_obj.LOG_LEVEL,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                "level": config_obj.LOG_LEVEL,
                "filename": str(log_path),
                "maxBytes": 5 * 1024 * 1024,
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console", "file"],
                "level": config_obj.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": config_obj.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console", "file"],
                "level": config_obj.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console", "file"],
                "level": config_obj.LOG_LEVEL,
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> Logger:
    """Retorna um logger com nome informado.

    Parâmetros:
        name (str): Nome do logger (ex.: __name__ ou "modulo.Classe").

    Retorna:
        Logger: Logger configurado com handlers de console e arquivo.
    """
    return logging.getLogger(name)
