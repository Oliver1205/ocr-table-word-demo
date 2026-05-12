"""Logging setup for console and optional file output."""

from __future__ import annotations

import logging
from pathlib import Path

from .config import DEFAULT_LOG_DIR, LOG_FILE_NAME
from .utils import ensure_dir


def setup_logger(
    name: str = "ocr_table_word_demo",
    log_dir: str | Path = DEFAULT_LOG_DIR,
    log_to_file: bool = True,
    level: int = logging.INFO,
) -> logging.Logger:
    """Create a project logger with readable console output."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_to_file:
        ensure_dir(log_dir)
        file_handler = logging.FileHandler(Path(log_dir) / LOG_FILE_NAME, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
