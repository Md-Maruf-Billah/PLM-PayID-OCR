"""Pattern extraction and the primary/secondary/whole-slip consensus algorithm.

Pure Python, no OpenCV/Tesseract dependency, so it can be unit tested without
a camera or the Tesseract binary.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

DEFAULT_PATTERN = r"^[A-Z]{8}$"


class Confidence(Enum):
    VERY_HIGH = "VERY_HIGH"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    NONE = "NONE"


@dataclass
class ScanResult:
    code: str | None
    confidence: Confidence
    reason: str

    @property
    def accepted(self) -> bool:
        return self.code is not None


def extract_code(raw_text: str, pattern: str = DEFAULT_PATTERN) -> str | None:
    """Extract a single code from a region OCR result (e.g. primary/secondary ROI)."""
    candidate = re.sub(r"[^A-Z]", "", raw_text.strip().upper())
    return candidate if re.fullmatch(pattern, candidate) else None


def extract_all_codes(full_text: str, pattern: str = DEFAULT_PATTERN) -> list[str]:
    """Extract every matching code found on the whole-slip OCR pass, line by line."""
    codes = []
    for line in full_text.splitlines():
        cleaned = re.sub(r"[^A-Z]", "", line.strip().upper())
        if re.fullmatch(pattern, cleaned):
            codes.append(cleaned)
    return codes


def resolve_code(
    primary: str | None,
    secondary: str | None,
    full_slip_codes: list[str] | None = None,
) -> ScanResult:
    """Apply the three-pass consensus rules.

    Priority: primary == secondary, then agreement with the whole-slip fallback,
    then a lone primary/secondary reading with no whole-slip signal to contradict
    it. Any disagreement between passes returns no code rather than guessing.
    """
    distinct_full = set(full_slip_codes or [])

    if primary and secondary:
        if primary == secondary:
            return ScanResult(primary, Confidence.VERY_HIGH, "primary and secondary codes match")
        return ScanResult(
            None, Confidence.NONE, f"primary/secondary disagree: {primary} vs {secondary}"
        )

    for label, candidate in (("primary", primary), ("secondary", secondary)):
        if not candidate:
            continue
        if not distinct_full:
            return ScanResult(
                candidate, Confidence.MEDIUM, f"{label} only, whole-slip OCR unavailable"
            )
        if candidate in distinct_full:
            return ScanResult(candidate, Confidence.HIGH, f"{label} confirmed by whole-slip OCR")
        return ScanResult(
            None,
            Confidence.NONE,
            f"{label} ({candidate}) conflicts with whole-slip OCR ({sorted(distinct_full)})",
        )

    if len(distinct_full) == 1:
        return ScanResult(
            next(iter(distinct_full)), Confidence.MEDIUM, "recovered from whole-slip OCR only"
        )
    if len(distinct_full) > 1:
        return ScanResult(
            None,
            Confidence.NONE,
            f"whole-slip OCR found conflicting codes: {sorted(distinct_full)}",
        )

    return ScanResult(None, Confidence.NONE, "no code detected in any pass")
