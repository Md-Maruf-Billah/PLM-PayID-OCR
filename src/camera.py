"""Webcam capture: open only for the duration of a scan, grab a few frames,
close immediately. See docs/setup.md for why we don't keep the stream open.
"""

from __future__ import annotations

import time

import cv2

from image_processor import Image


class CameraError(RuntimeError):
    pass


def capture_frames(
    device_index: int,
    frame_count: int,
    frame_interval_ms: int,
    warmup_ms: int,
    resolution: tuple[int, int] | None = None,
) -> list[Image]:
    cap = cv2.VideoCapture(device_index)
    if not cap.isOpened():
        raise CameraError(f"could not open camera at index {device_index}")

    try:
        if resolution:
            width, height = resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        time.sleep(warmup_ms / 1000)

        frames = []
        for i in range(frame_count):
            ok, frame = cap.read()
            if not ok:
                raise CameraError(f"failed to read frame {i + 1}/{frame_count}")
            frames.append(frame)
            if i < frame_count - 1:
                time.sleep(frame_interval_ms / 1000)

        return frames
    finally:
        cap.release()
