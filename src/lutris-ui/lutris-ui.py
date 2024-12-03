#!/usr/bin/env python3

import pygame

from lutrisuiapp import LutrisUiApp
from settings import Settings
from uiwidgets import Controls

REPEATABLE = ("UP", "DOWN", "LEFT", "RIGHT")

KBD_MAP = {pygame.K_UP: "UP", pygame.K_DOWN: "DOWN", pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT",
           pygame.K_RETURN: "ENTER", pygame.K_ESCAPE: "EXIT", pygame.K_r: "RELOAD"}

JOY_MAP = {pygame.CONTROLLER_BUTTON_A: "ENTER", pygame.CONTROLLER_BUTTON_START: "ENTER",
           pygame.CONTROLLER_BUTTON_DPAD_UP: "UP", pygame.CONTROLLER_BUTTON_DPAD_DOWN: "DOWN",
           pygame.CONTROLLER_BUTTON_DPAD_LEFT: "LEFT", pygame.CONTROLLER_BUTTON_DPAD_RIGHT: "RIGHT"}

if __name__ == '__main__':
    ctr = Controls(repeatable_commands=("UP", "DOWN", "LEFT", "RIGHT"),
                   keyboard_commands={
                       pygame.K_UP: "UP", pygame.K_DOWN: "DOWN", pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT",
                       pygame.K_RETURN: "ENTER",
                       pygame.K_ESCAPE: "EXIT",
                       pygame.K_r: "RELOAD"},
                   joypad_keys_commands={
                       pygame.CONTROLLER_BUTTON_A: "ENTER",
                       pygame.CONTROLLER_BUTTON_START: "ENTER",
                       pygame.CONTROLLER_BUTTON_DPAD_UP: "UP",
                       pygame.CONTROLLER_BUTTON_DPAD_DOWN: "DOWN",
                       pygame.CONTROLLER_BUTTON_DPAD_LEFT: "LEFT",
                       pygame.CONTROLLER_BUTTON_DPAD_RIGHT: "RIGHT"},
                   allowed_event_types=(pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN,
                                        pygame.MOUSEMOTION, pygame.MOUSEWHEEL,
                                        pygame.WINDOWSIZECHANGED, pygame.WINDOWRESTORED, pygame.QUIT))
    app = LutrisUiApp(ctr)
    app.run()
    Settings.save()
