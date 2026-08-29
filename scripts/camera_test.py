"""Standalone camera smoke test: capture a few frames, print sharpness scores,
save the sharpest one to captures/preview.jpg (gitignored) for a quick look.

Usage: python scripts/camera_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import cv2

from camera import capture_frames
from config import PROJECT_ROOT, config
from image_processor import select_sharpest, sharpness


def main() -> None:
    cam_cfg = config["camera"]
    frames = capture_frames(
        device_index=cam_cfg["device_index"],
        frame_count=cam_cfg["frame_count"],
        frame_interval_ms=cam_cfg["frame_interval_ms"],
        warmup_ms=cam_cfg["warmup_ms"],
        resolution=(cam_cfg["resolution"]["width"], cam_cfg["resolution"]["height"]),
    )

    for i, frame in enumerate(frames):
        print(f"frame {i}: sharpness={sharpness(frame):.1f}")

    best = select_sharpest(frames)
    out_dir = PROJECT_ROOT / "captures"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "preview.jpg"
    cv2.imwrite(str(out_path), best)
    print(f"saved sharpest frame to {out_path}")


if __name__ == "__main__":
    main()
