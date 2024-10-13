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
        super().__init__(bg_color=pygame.Color(255, 255, 255))
        ldb = LutrisDb()
        self.games_viewport = UiGameListWidget(self, ldb, size_w=-10, size_h=-10,
                                               pos_x_type=DynamicTypes.TYPE_CENTER, pos_y_type=DynamicTypes.TYPE_CENTER)
        self.game_is_running = UiGameIsRunningWidget(self, ldb, pos_x_type=DynamicTypes.TYPE_CENTER,
                                                     pos_y_type=DynamicTypes.TYPE_CENTER,
                                                     size_w=GAME_WIDGET_WIDTH, size_h=GAME_WIDGET_HEIGHT + 60)

    def init_display_settings(self):
        if "--fullscreen" in sys.argv or "-f" in sys.argv:
            self.fullscreen = True
        else:
            self.fullscreen = self.settings.get("fullscreen", False)

        if "--noframe" in sys.argv or "-n" in sys.argv:
            self.noframe = True
        else:
            self.noframe = self.settings.get("noframe", False)

        self.size_w = self.settings.get("size_w", 0)
        self.size_h = self.settings.get("size_h", 0)

        super().init_display_settings()
        pygame.display.set_caption("Lutris-UI")

    def process_events(self, events: list, pos: (int, int) = None) -> bool:
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN and e.mod == pygame.KMOD_LALT:
                pygame.display.toggle_fullscreen()
                return True
        return super().process_events(events, pos)
