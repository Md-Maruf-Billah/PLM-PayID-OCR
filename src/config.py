"""Loads and exposes the project configuration.

config/local.json (gitignored) overrides config/config.json when present,
so machine-specific settings (camera index, ROI calibration) never need
to touch the tracked defaults.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.json"
LOCAL_CONFIG_PATH = PROJECT_ROOT / "config" / "local.json"


def _deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(
    default_path: Path = DEFAULT_CONFIG_PATH,
    local_path: Path = LOCAL_CONFIG_PATH,
) -> dict[str, Any]:
    with open(default_path, encoding="utf-8") as f:
        config = json.load(f)

    if local_path.exists():
        with open(local_path, encoding="utf-8") as f:
            config = _deep_merge(config, json.load(f))

    return config


config = load_config()
