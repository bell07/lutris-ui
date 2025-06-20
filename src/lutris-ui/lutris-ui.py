#!/usr/bin/env python3

from __future__ import annotations

from lutrisuiapp import LutrisUiApp
from pygame import constants
from settings import Settings
from uiwidgets import Controls

if __name__ == "__main__":
    ctr = Controls(
        repeatable_commands=["UP", "DOWN", "LEFT", "RIGHT"],
        keyboard_commands={
            constants.K_UP: "UP",
            constants.K_DOWN: "DOWN",
            constants.K_LEFT: "LEFT",
            constants.K_RIGHT: "RIGHT",
            constants.K_RETURN: "ENTER",
            constants.K_BACKSPACE: "BACK",
            constants.K_ESCAPE: "EXIT",
            constants.K_r: "RELOAD",
        },
        joypad_keys_commands={
            constants.CONTROLLER_BUTTON_A: "ENTER",
            constants.CONTROLLER_BUTTON_START: "ENTER",
            constants.CONTROLLER_BUTTON_B: "BACK",
            constants.CONTROLLER_BUTTON_BACK: "BACK",
            constants.CONTROLLER_BUTTON_DPAD_UP: "UP",
            constants.CONTROLLER_BUTTON_DPAD_DOWN: "DOWN",
            constants.CONTROLLER_BUTTON_DPAD_LEFT: "LEFT",
            constants.CONTROLLER_BUTTON_DPAD_RIGHT: "RIGHT",
        },
        allowed_event_types=[
            constants.MOUSEBUTTONUP,
            constants.MOUSEBUTTONDOWN,
            constants.MOUSEMOTION,
            constants.MOUSEWHEEL,
            constants.WINDOWSIZECHANGED,
            constants.WINDOWRESTORED,
            constants.QUIT,
        ],
    )
    app = LutrisUiApp(ctr)
    app.run()
    Settings.save()
