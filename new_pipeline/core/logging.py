import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from new_pipeline.config import get_config


def configure_logging() -> logging.Logger:
    config = get_config()
    log_file_path = Path(config.logging.log_file).resolve()
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("quantum_avenger")
    logger.setLevel(getattr(logging, config.logging.level.upper(), logging.INFO))

    formatter = logging.Formatter(config.logging.format)
    handler = RotatingFileHandler(
        filename=log_file_path,
        maxBytes=config.logging.max_bytes,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger
