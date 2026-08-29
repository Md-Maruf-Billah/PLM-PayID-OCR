"""End-to-end test: renders a synthetic PayID-style slip (never a real customer
scan -- see .gitignore) and runs it through the actual image_processor + ocr +
code_detector pipeline. Skipped automatically if the Tesseract binary isn't
installed on this machine.
"""

from __future__ import annotations

import shutil

import numpy as np
import pytest
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont

from code_detector import extract_all_codes, extract_code, resolve_code
from ocr import read_full_slip, read_region

pytestmark = pytest.mark.skipif(shutil.which("tesseract") is None, reason="tesseract not installed")

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CODE = "YABORKFH"

PRIMARY_ROI = (0.05, 0.05, 0.90, 0.20)
SECONDARY_ROI = (0.05, 0.55, 0.90, 0.20)


def render_slip(code: str) -> np.ndarray:
    img = PILImage.new("RGB", (900, 700), color="white")
    draw = ImageDraw.Draw(img)
    big_font = ImageFont.truetype(FONT_PATH, 60)
    small_font = ImageFont.truetype(FONT_PATH, 28)

    draw.text((60, 40), "PLAYLIVE", font=small_font, fill="black")
    draw.text((60, 90), code, font=big_font, fill="black")
    draw.text((60, 260), "HOW TO DEPOSIT", font=small_font, fill="black")
    draw.text((60, 310), "OPEN YOUR MOBILE BANKING APP", font=small_font, fill="black")
    draw.text((60, 360), "SEND FUNDS USING CODE", font=small_font, fill="black")
    draw.text((60, 400), code, font=big_font, fill="black")
    draw.text((60, 560), "HAND THIS SLIP TO OUR CASHIER", font=small_font, fill="black")

    return np.array(img)[:, :, ::-1].copy()  # RGB -> BGR for OpenCV/pytesseract parity


@pytest.fixture
def slip_image():
    return render_slip(CODE)


def test_primary_region_reads_code(slip_image):
    text = read_region(
        slip_image, PRIMARY_ROI, whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ", psm=6, lang="eng",
        blur_kernel=3, resize_scale=2.0,
    )
    assert extract_code(text) == CODE


def test_secondary_region_reads_code(slip_image):
    text = read_region(
        slip_image, SECONDARY_ROI, whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ", psm=6, lang="eng",
        blur_kernel=3, resize_scale=2.0,
    )
    assert extract_code(text) == CODE


def test_full_pipeline_resolves_via_consensus(slip_image):
    primary_text = read_region(
        slip_image, PRIMARY_ROI, whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ", psm=6, lang="eng",
        blur_kernel=3, resize_scale=2.0,
    )
    secondary_text = read_region(
        slip_image, SECONDARY_ROI, whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ", psm=6, lang="eng",
        blur_kernel=3, resize_scale=2.0,
    )
    full_text = read_full_slip(
        slip_image, whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ", psm=6, lang="eng",
        blur_kernel=3, resize_scale=2.0,
    )

    primary = extract_code(primary_text)
    secondary = extract_code(secondary_text)
    full_codes = extract_all_codes(full_text)

    result = resolve_code(primary, secondary, full_codes)

    assert result.accepted
    assert result.code == CODE
