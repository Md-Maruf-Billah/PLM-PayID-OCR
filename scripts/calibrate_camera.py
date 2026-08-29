"""Interactive ROI calibration: captures a frame, then for the primary and
secondary code regions, click-drag a rectangle over the printed code. Prints
the resulting ROI fractions to paste into config/local.json.

Usage: python scripts/calibrate_camera.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import cv2

from camera import capture_frames
from config import config
from image_processor import select_sharpest

_drag_state: dict = {}


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
            raise SystemExit("calibration cancelled")

    x0, y0 = _drag_state["start"]
    x1, y1 = _drag_state["end"]
    x_min, x_max = sorted((x0, x1))
    y_min, y_max = sorted((y0, y1))

    return (x_min / width, y_min / height, (x_max - x_min) / width, (y_max - y_min) / height)


def main() -> None:
    cam_cfg = config["camera"]
    frames = capture_frames(
        device_index=cam_cfg["device_index"],
        frame_count=cam_cfg["frame_count"],
        frame_interval_ms=cam_cfg["frame_interval_ms"],
        warmup_ms=cam_cfg["warmup_ms"],
        resolution=(cam_cfg["resolution"]["width"], cam_cfg["resolution"]["height"]),
    )
    frame = select_sharpest(frames)

    window = "Calibrate - drag a box, Enter to confirm, Esc to cancel"
    cv2.namedWindow(window)
    cv2.setMouseCallback(window, _on_mouse)

    print("Drag a rectangle over the PRIMARY (top) code, then press Enter.")
    primary_roi = _pick_region(window, frame)

    print("Drag a rectangle over the SECONDARY code, then press Enter.")
    secondary_roi = _pick_region(window, frame)

    cv2.destroyAllWindows()

    print("\nPaste into config/local.json:")
    print(
        '{\n'
        '  "regions": {\n'
        f'    "primary": {{ "roi": {[round(v, 4) for v in primary_roi]} }},\n'
        f'    "secondary": {{ "roi": {[round(v, 4) for v in secondary_roi]} }}\n'
        '  }\n'
        '}'
    )


if __name__ == "__main__":
    main()
