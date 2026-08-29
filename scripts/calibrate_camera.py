"""Interactive ROI calibration CLI. See src/calibration.py for the shared
implementation also used by the packaged app's first-run setup and its
"Recalibrate" menu item.

Usage: python scripts/calibrate_camera.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from calibration import CalibrationCancelled, local_config_path, run_calibration


def main() -> None:
    try:
        regions = run_calibration()
    except CalibrationCancelled:
        print("Calibration cancelled.")
        raise SystemExit(1)

    print(f"\nSaved to {local_config_path()}:")
    print(regions)


if __name__ == "__main__":
    main()
