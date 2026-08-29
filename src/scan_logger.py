"""Scan history logging. Never logs images or transaction details -- only the
resolved code (optionally masked) and the outcome, per docs/setup.md privacy notes.
"""

from __future__ import annotations

import logging

from runtime_paths import user_data_dir

_logger = logging.getLogger("payid_ocr")


def _mask(code: str) -> str:
    return "*" * (len(code) - 3) + code[-3:]


def setup_logging(log_dir: str, log_file: str) -> logging.Logger:
    if _logger.handlers:
        return _logger

    directory = user_data_dir() / log_dir
    directory.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(directory / log_file)
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

    _logger.setLevel(logging.INFO)
    _logger.addHandler(handler)
    _logger.addHandler(logging.StreamHandler())
    return _logger


def log_success(code: str, confidence: str, mask_codes: bool = False) -> None:
    shown = _mask(code) if mask_codes else code
    _logger.info("SCAN_SUCCESS %s confidence=%s", shown, confidence)


def log_failure(reason: str) -> None:
    _logger.info("SCAN_FAILED %s", reason)
