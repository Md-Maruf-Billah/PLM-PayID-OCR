"""Plays the success/failure cue. Uses macOS afplay when available, falling
back to the terminal bell so the script still gives audible feedback on
other platforms during development.
"""

from __future__ import annotations

import subprocess
import sys

from runtime_paths import bundle_root


def _play(path: str) -> None:
    full_path = bundle_root() / path
    if sys.platform == "darwin" and full_path.exists():
        subprocess.run(["afplay", str(full_path)], check=False)
    else:
        print("\a", end="", flush=True)


def play_success(sound_path: str) -> None:
    _play(sound_path)


def play_failure(sound_path: str) -> None:
    _play(sound_path)
