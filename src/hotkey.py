"""Global F8 listener. Each trigger runs the callback on its own background
thread so a slow scan never blocks the listener. app.py guards against
overlapping scans if F8 is pressed again before the previous one finishes.
"""

from __future__ import annotations

import threading
from typing import Callable

from pynput import keyboard

HOTKEY = "<f8>"


class HotkeyListener:
    def __init__(self, on_trigger: Callable[[], None]):
        self._on_trigger = on_trigger
        self._listener: keyboard.GlobalHotKeys | None = None

    def _fire(self) -> None:
        threading.Thread(target=self._on_trigger, daemon=True).start()

    def start(self) -> None:
        self._listener = keyboard.GlobalHotKeys({HOTKEY: self._fire})
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
