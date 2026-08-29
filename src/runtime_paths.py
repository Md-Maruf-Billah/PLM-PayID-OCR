"""Path resolution that differs between running from source and running as a
PyInstaller-frozen .app bundle (bundle contents are read-only once installed,
so writable data -- calibration, logs -- lives under the user's Application
Support directory instead).
"""

from __future__ import annotations

import sys
from pathlib import Path

APP_NAME = "PlayLive PayID Scanner"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def bundle_root() -> Path:
    """Read-only resources shipped with the app: default config, bundled
    tesseract binary/tessdata, sound assets. The project root in dev."""
    if is_frozen():
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent


def user_data_dir() -> Path:
    """Writable per-user directory for calibration overrides and logs."""
    base = Path.home() / "Library" / "Application Support" / APP_NAME
    base.mkdir(parents=True, exist_ok=True)
    return base


def bundled_tesseract_cmd() -> str | None:
    if not is_frozen():
        return None
    candidate = bundle_root() / "tesseract-bin" / "tesseract"
    return str(candidate) if candidate.exists() else None


def bundled_tessdata_dir() -> str | None:
    if not is_frozen():
        return None
    candidate = bundle_root() / "tessdata"
    return str(candidate) if candidate.exists() else None
