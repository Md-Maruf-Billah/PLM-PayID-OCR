"""Menu bar app: the packaged product. Registers the global F8 hotkey, walks
the user through calibration on first launch, and offers Recalibrate/Open
Logs from the menu bar icon. Built into PlayLive PayID Scanner.app via
scripts/build_app.sh -- see packaging/PlayLivePayIDScanner.spec.

macOS only (rumps wraps PyObjC/Cocoa); not importable on other platforms.
"""

from __future__ import annotations

import subprocess
import threading

import rumps

from calibration import calibration_exists, run_calibration
from hotkey import HotkeyListener
from main import scan
from runtime_paths import user_data_dir

_scan_lock = threading.Lock()


class PayIDScannerApp(rumps.App):
    def __init__(self):
        super().__init__("PayID Scanner", quit_button="Quit")
        self.menu = ["Recalibrate", "Open Logs Folder"]
        self._hotkey = HotkeyListener(self._on_hotkey)

    def _on_hotkey(self) -> None:
        if not _scan_lock.acquire(blocking=False):
            return  # a scan is already in progress; ignore the extra F8 press
        try:
            scan()
        except Exception as exc:  # noqa: BLE001 - surface any failure to the cashier
            rumps.notification("PayID Scanner", "Scan failed", str(exc))
        finally:
            _scan_lock.release()

    @rumps.clicked("Recalibrate")
    def recalibrate(self, _sender) -> None:
        run_calibration()
        rumps.notification("PayID Scanner", "Calibration saved", "F8 is ready to use.")

    @rumps.clicked("Open Logs Folder")
    def open_logs(self, _sender) -> None:
        subprocess.run(["open", str(user_data_dir())], check=False)

    def launch(self) -> None:
        if not calibration_exists():
            rumps.alert(
                title="First-time setup",
                message=(
                    "Let's calibrate the camera before the F8 shortcut is ready.\n\n"
                    "Click OK, then place a test slip under the camera and follow "
                    "the on-screen prompts."
                ),
            )
            run_calibration()
        self._hotkey.start()
        self.run()


def main() -> None:
    PayIDScannerApp().launch()


if __name__ == "__main__":
    main()
