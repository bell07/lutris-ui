import sys

import pygame

from lutrisdb import LutrisDb
from settings import Settings
from uigamelist import UiGameListWidget, GAME_WIDGET_WIDTH, GAME_WIDGET_HEIGHT
from uirunninggame import UiGameIsRunningWidget
from uiwidgets import DynamicTypes, UiApp


class LutrisUiApp(UiApp):
    def __init__(self):
        self.settings = Settings("window")

        if "--fullscreen" in sys.argv or "-f" in sys.argv:
            fullscreen = True
        else:
            fullscreen = self.settings.get("fullscreen", False)

        if "--noframe" in sys.argv or "-n" in sys.argv:
            noframe = True
        else:
            noframe = self.settings.get("noframe", False)

        size_w = self.settings.get("size_w", 0)
        size_h = self.settings.get("size_h", 0)
        super().__init__(size_w=size_w, size_h=size_h, fullscreen=fullscreen, noframe=noframe)
        pygame.display.set_caption("Lutris-UI")
        ldb = LutrisDb()
        self.games_viewport = UiGameListWidget(self, ldb, border_all=10, border_color="Grey")
        self.game_is_running = UiGameIsRunningWidget(self, ldb, pos_x_type=DynamicTypes.TYPE_CENTER,
                                                     pos_y_type=DynamicTypes.TYPE_CENTER,
                                                     size_w=GAME_WIDGET_WIDTH, size_h=GAME_WIDGET_HEIGHT + 60)

    def process_events(self, events: list, pos: (int, int) = None) -> bool:
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN and e.mod == pygame.KMOD_LALT:
                self.fullscreen = not self.fullscreen
                self.init_display_settings(reset=True)
                return True
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN and e.mod == pygame.KMOD_RALT:
                self.noframe = not self.noframe
                self.fullscreen = False
                self.init_display_settings(reset=True)
                return True
            if e.type == pygame.KEYDOWN and e.key == pygame.K_UP and e.mod == pygame.KMOD_LALT:
                self.init_display_settings()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_DOWN and e.mod == pygame.KMOD_LALT:
                pygame.display.iconify()
                return True

        return super().process_events(events, pos)
