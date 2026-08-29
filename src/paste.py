"""Copies the resolved code to the clipboard and pastes it into whichever field
the cashier already has focused. Never clicks or moves focus itself.
"""

from __future__ import annotations

import sys

import pyperclip
from pynput.keyboard import Controller, Key

_MODIFIER = Key.cmd if sys.platform == "darwin" else Key.ctrl


def copy_to_clipboard(code: str) -> None:
    pyperclip.copy(code)


def paste_into_active_field(auto_submit: bool = False) -> None:
    keyboard = Controller()
    with keyboard.pressed(_MODIFIER):
        keyboard.tap("v")
    if auto_submit:
        keyboard.tap(Key.enter)
