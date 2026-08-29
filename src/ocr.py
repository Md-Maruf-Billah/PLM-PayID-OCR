"""pytesseract wrapper for the three OCR passes: primary region, secondary region,
and whole slip.
"""

from __future__ import annotations

import pytesseract

from image_processor import Image, crop_roi, preprocess_for_ocr


def _tesseract_config(whitelist: str, psm: int) -> str:
    return f'--psm {psm} -c tessedit_char_whitelist={whitelist}'


def read_region(
    image: Image,
    roi: tuple[float, float, float, float],
    whitelist: str,
    psm: int,
    lang: str,
    blur_kernel: int,
    resize_scale: float,
) -> str:
    cropped = crop_roi(image, roi)
    processed = preprocess_for_ocr(cropped, blur_kernel=blur_kernel, resize_scale=resize_scale)
    return pytesseract.image_to_string(
        processed, lang=lang, config=_tesseract_config(whitelist, psm)
    )


def read_full_slip(
    image: Image,
    whitelist: str,
    psm: int,
    lang: str,
    blur_kernel: int,
    resize_scale: float,
) -> str:
    processed = preprocess_for_ocr(image, blur_kernel=blur_kernel, resize_scale=resize_scale)
    return pytesseract.image_to_string(
        processed, lang=lang, config=_tesseract_config(whitelist, psm)
    )
