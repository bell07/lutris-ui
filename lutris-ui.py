#!/usr/bin/env python3

import pygame

from controls import Controls
from lutrisuiapp import LutrisUiApp
from settings import Settings

if __name__ == '__main__':
    app = LutrisUiApp()
    ctr = Controls()

    while True:
        ctr.update_controls()
        if app.process_tick(ctr.get_tick_time()) is False:
            break
        if app.process_events(ctr.events) is False:
            break
        app.draw()
        ctr.game_tick()

    Settings.save()
    pygame.quit()
