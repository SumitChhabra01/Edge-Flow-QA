"""Logging utilities for EdgeQA."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Optional


def _ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def get_logger(name: str, logs_dir: str = "logs", level: int = logging.INFO) -> logging.Logger:
    """Create or return a configured logger with file and console handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    _ensure_dir(logs_dir)
    logger.setLevel(level)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(logs_dir, f"{name}_{timestamp}.log")

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger
