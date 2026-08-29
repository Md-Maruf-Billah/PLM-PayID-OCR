"""Interactive ROI calibration, shared by scripts/calibrate_camera.py (dev
CLI) and src/app.py (first-run setup + the "Recalibrate" menu item).

Click-drag a rectangle over the primary code, then the secondary code; the
result is written to the per-user local.json (see runtime_paths) so it
overrides the guessed defaults in config/config.json without touching them.
"""

from __future__ import annotations

import json
import os
import tempfile

import cv2

from camera import capture_frames
from config import LOCAL_CONFIG_PATH, config
from image_processor import select_sharpest

_drag_state: dict = {}


class CalibrationCancelled(Exception):
    """Raised when the user presses Esc during region picking."""


def local_config_path():
    return LOCAL_CONFIG_PATH


def calibration_exists() -> bool:
    return LOCAL_CONFIG_PATH.exists()


def _on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        _drag_state["start"] = (x, y)
        _drag_state["end"] = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE and "start" in _drag_state and flags & cv2.EVENT_FLAG_LBUTTON:
        _drag_state["end"] = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        _drag_state["end"] = (x, y)
        _drag_state["done"] = True


def _pick_region(window: str, frame) -> tuple[float, float, float, float]:
    global _drag_state
    _drag_state = {}
    height, width = frame.shape[:2]

    while True:
        display = frame.copy()
        if "start" in _drag_state:
            cv2.rectangle(display, _drag_state["start"], _drag_state["end"], (0, 255, 0), 2)
        cv2.imshow(window, display)
        key = cv2.waitKey(20)
        if _drag_state.get("done") or key == 13:
            break
        if key == 27:
            raise CalibrationCancelled("calibration cancelled")

    x0, y0 = _drag_state["start"]
    x1, y1 = _drag_state["end"]
    x_min, x_max = sorted((x0, x1))
    y_min, y_max = sorted((y0, y1))

    return (x_min / width, y_min / height, (x_max - x_min) / width, (y_max - y_min) / height)


def _capture_reference_frame():
    cam_cfg = config["camera"]
    frames = capture_frames(
        device_index=cam_cfg["device_index"],
        frame_count=cam_cfg["frame_count"],
        frame_interval_ms=cam_cfg["frame_interval_ms"],
        warmup_ms=cam_cfg["warmup_ms"],
        resolution=(cam_cfg["resolution"]["width"], cam_cfg["resolution"]["height"]),
    )
    return select_sharpest(frames)


def run_calibration() -> dict:
    """Runs the interactive picker and writes the result to local.json.
    Returns the {"primary": roi, "secondary": roi} dict that was saved.
    """
    frame = _capture_reference_frame()

    window = "Calibrate - drag a box, Enter to confirm, Esc to cancel"
    cv2.namedWindow(window)
    cv2.setMouseCallback(window, _on_mouse)

    try:
        print("Drag a rectangle over the PRIMARY (top) code, then press Enter.")
        primary_roi = _pick_region(window, frame)

        print("Drag a rectangle over the SECONDARY code, then press Enter.")
        secondary_roi = _pick_region(window, frame)
    finally:
        cv2.destroyAllWindows()

    regions = {
        "primary": [round(v, 4) for v in primary_roi],
        "secondary": [round(v, 4) for v in secondary_roi],
    }
    save_regions(regions)
    return regions


def save_regions(regions: dict) -> None:
    existing = {}
    if LOCAL_CONFIG_PATH.exists():
        try:
            with open(LOCAL_CONFIG_PATH, encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                existing = loaded
        except (json.JSONDecodeError, OSError):
            pass  # corrupted -- overwrite it with a fresh file below

    existing.setdefault("regions", {})
    existing["regions"]["primary"] = {"roi": regions["primary"]}
    existing["regions"]["secondary"] = {"roi": regions["secondary"]}

    LOCAL_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=LOCAL_CONFIG_PATH.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)
        os.replace(tmp_path, LOCAL_CONFIG_PATH)
    except BaseException:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise
