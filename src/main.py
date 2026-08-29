"""Entry point invoked by the F8 hotkey (see docs/setup.md for the Hammerspoon
binding). Captures a slip, runs the three OCR passes, resolves a code via
consensus, and pastes it into whichever field the cashier has focused.
"""

from __future__ import annotations

from camera import CameraError, capture_frames
from code_detector import extract_all_codes, extract_code, resolve_code
from config import config
from image_processor import select_sharpest
from ocr import read_full_slip, read_region
from paste import copy_to_clipboard, paste_into_active_field
from scan_logger import log_failure, log_success, setup_logging
from sounds import play_failure, play_success


def scan() -> None:
    setup_logging(config["logging"]["log_dir"], config["logging"]["log_file"])

    cam_cfg = config["camera"]
    try:
        frames = capture_frames(
            device_index=cam_cfg["device_index"],
            frame_count=cam_cfg["frame_count"],
            frame_interval_ms=cam_cfg["frame_interval_ms"],
            warmup_ms=cam_cfg["warmup_ms"],
            resolution=(cam_cfg["resolution"]["width"], cam_cfg["resolution"]["height"]),
        )
    except CameraError as exc:
        log_failure(f"CAMERA_ERROR {exc}")
        play_failure(config["sounds"]["failure"])
        print("SCAN AGAIN (camera error)")
        return

    frame = select_sharpest(frames)

    ocr_cfg = config["ocr"]
    pre_cfg = config["preprocessing"]

    primary_text = read_region(
        frame,
        roi=config["regions"]["primary"]["roi"],
        whitelist=ocr_cfg["whitelist"],
        psm=ocr_cfg["psm_region"],
        lang=ocr_cfg["lang"],
        blur_kernel=pre_cfg["gaussian_blur_kernel"],
        resize_scale=pre_cfg["resize_scale"],
    )
    secondary_text = read_region(
        frame,
        roi=config["regions"]["secondary"]["roi"],
        whitelist=ocr_cfg["whitelist"],
        psm=ocr_cfg["psm_region"],
        lang=ocr_cfg["lang"],
        blur_kernel=pre_cfg["gaussian_blur_kernel"],
        resize_scale=pre_cfg["resize_scale"],
    )
    full_text = read_full_slip(
        frame,
        whitelist=ocr_cfg["whitelist"],
        psm=ocr_cfg["psm_full_slip"],
        lang=ocr_cfg["lang"],
        blur_kernel=pre_cfg["gaussian_blur_kernel"],
        resize_scale=pre_cfg["resize_scale"],
    )

    primary = extract_code(primary_text, ocr_cfg["code_pattern"])
    secondary = extract_code(secondary_text, ocr_cfg["code_pattern"])
    full_slip_codes = extract_all_codes(full_text, ocr_cfg["code_pattern"])

    result = resolve_code(primary, secondary, full_slip_codes)

    if not result.accepted:
        log_failure(result.reason)
        play_failure(config["sounds"]["failure"])
        print("SCAN AGAIN")
        return

    try:
        copy_to_clipboard(result.code)
        paste_into_active_field(auto_submit=config["paste"]["auto_submit"])
    except Exception as exc:
        log_failure(f"PASTE_ERROR {exc}")
        play_failure(config["sounds"]["failure"])
        print(f"SCAN AGAIN (could not paste: {exc})")
        return

    log_success(result.code, result.confidence.value, mask_codes=config["logging"]["mask_codes"])
    play_success(config["sounds"]["success"])
    print(result.code)


if __name__ == "__main__":
    scan()
