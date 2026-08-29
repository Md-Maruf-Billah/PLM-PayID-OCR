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

from calibration import CalibrationCancelled, calibration_exists, run_calibration
from camera import CameraError
from hotkey import HotkeyListener
from main import scan
from runtime_paths import user_data_dir
from scan_logger import log_failure, setup_logging

_scan_lock = threading.Lock()


class PayIDScannerApp(rumps.App):
    def __init__(self):
        super().__init__("PayID Scanner", quit_button="Quit")
        self.menu = ["Recalibrate", "Open Logs Folder"]
        self._hotkey = HotkeyListener(self._on_hotkey)
        # Calibration pops a modal alert and the hotkey needs Accessibility
        # permission -- both are safer run once the Cocoa event loop (from
        # self.run(), below) is actually pumping, not before it starts.
        self._startup_timer = rumps.Timer(self._on_startup, 1)

    def _on_startup(self, _timer) -> None:
        self._startup_timer.stop()
        if not calibration_exists():
            rumps.alert(
                title="First-time setup",
                message=(
                    "Let's calibrate the camera before the F8 shortcut is ready.\n\n"
                    "Click OK, then place a test slip under the camera and follow "
                    "the on-screen prompts."
                ),
            )
            if not self._run_calibration_safely(notify_on_success=False):
                return  # left uncalibrated; they can retry from the menu
        self._start_hotkey()

    def _run_calibration_safely(self, notify_on_success: bool = True) -> bool:
        try:
            run_calibration()
        except CalibrationCancelled:
            rumps.alert(
                title="Calibration cancelled",
                message="Recalibrate from the menu bar icon whenever you're ready.",
            )
            return False
        except CameraError as exc:
            rumps.alert(
                title="Camera error",
                message=f"Couldn't read the camera: {exc}\n\n"
                "Check it's connected, then try Recalibrate from the menu.",
            )
            return False
        except Exception as exc:  # noqa: BLE001 - never let this take the app down
            rumps.alert(title="Calibration failed", message=str(exc))
            return False

        if notify_on_success:
            rumps.notification("PayID Scanner", "Calibration saved", "F8 is ready to use.")
        return True

    def _start_hotkey(self) -> None:
        try:
            self._hotkey.start()
        except Exception as exc:  # noqa: BLE001 - never let this take the app down
            rumps.alert(
                title="F8 shortcut couldn't start",
                message=(
                    f"{exc}\n\n"
                    "This is usually a missing Accessibility permission. Grant it in "
                    "System Settings -> Privacy & Security -> Accessibility, then quit "
                    "and reopen this app."
                ),
            )

    def _on_hotkey(self) -> None:
        if not _scan_lock.acquire(blocking=False):
            return  # a scan is already in progress; ignore the extra F8 press
        try:
            scan()
        except Exception as exc:  # noqa: BLE001 - surface any failure to the cashier
            log_failure(f"UNEXPECTED_ERROR {exc}")
            rumps.notification("PayID Scanner", "Scan failed", str(exc))
        finally:
            _scan_lock.release()

    @rumps.clicked("Recalibrate")
    def recalibrate(self, _sender) -> None:
        self._run_calibration_safely()

    @rumps.clicked("Open Logs Folder")
    def open_logs(self, _sender) -> None:
        subprocess.run(["open", str(user_data_dir())], check=False)

    def launch(self) -> None:
        setup_logging("logs", "scan_history.log")
        self._startup_timer.start()
        self.run()


def main() -> None:
    PayIDScannerApp().launch()


if __name__ == "__main__":
    main()
