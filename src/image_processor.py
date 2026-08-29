"""OpenCV preprocessing: cropping regions of interest and cleaning images for OCR."""

from __future__ import annotations

import cv2
import numpy as np

Image = np.ndarray


def crop_roi(image: Image, roi: tuple[float, float, float, float]) -> Image:
    """Crop a region given as fractions of image size: (x, y, w, h), each in [0, 1]."""
    height, width = image.shape[:2]
    x, y, w, h = roi
    x0 = int(x * width)
    y0 = int(y * height)
    x1 = int((x + w) * width)
    y1 = int((y + h) * height)
    return image[y0:y1, x0:x1]


def sharpness(image: Image) -> float:
    """Higher is sharper. Used to pick the best of several captured frames."""
    gray = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def select_sharpest(frames: list[Image]) -> Image:
    if not frames:
        raise ValueError("no frames to select from")
    return max(frames, key=sharpness)


def preprocess_for_ocr(
    image: Image,
    blur_kernel: int = 3,
    resize_scale: float = 2.0,
) -> Image:
    """Grayscale -> blur -> Otsu threshold -> upscale, the standard pipeline for
    printed dark-text-on-light-paper slips.
    """
    gray = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if blur_kernel > 0:
        k = blur_kernel if blur_kernel % 2 == 1 else blur_kernel + 1
        gray = cv2.GaussianBlur(gray, (k, k), 0)

    _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    if resize_scale and resize_scale != 1.0:
        thresholded = cv2.resize(
            thresholded,
            None,
            fx=resize_scale,
            fy=resize_scale,
            interpolation=cv2.INTER_CUBIC,
        )

    return thresholded
