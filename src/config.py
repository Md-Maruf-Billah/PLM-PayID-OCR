"""Loads and exposes the project configuration.

A per-user local.json (see runtime_paths.user_data_dir) overrides
config/config.json when present, so machine-specific settings (camera
index, calibrated ROIs) never touch the tracked defaults -- and, once
bundled into a read-only .app, have somewhere writable to live at all.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from runtime_paths import bundle_root, user_data_dir

PROJECT_ROOT = bundle_root()
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.json"
LOCAL_CONFIG_PATH = user_data_dir() / "local.json"


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
        try:
            with open(local_path, encoding="utf-8") as f:
                local_overrides = json.load(f)
            if not isinstance(local_overrides, dict):
                raise ValueError(f"expected a JSON object, got {type(local_overrides).__name__}")
            config = _deep_merge(config, local_overrides)
        except (json.JSONDecodeError, ValueError, OSError) as exc:
            # A corrupted local.json (e.g. from a crash mid-write) must never take
            # the whole app down on every launch -- fall back to defaults and let
            # the user recalibrate from the menu to fix it.
            print(
                f"WARNING: ignoring corrupted {local_path} ({exc}); using default config.",
                file=sys.stderr,
            )

    return config


config = load_config()
