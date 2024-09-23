import sys

import pygame

from lutrisdb import LutrisDb
from uigamelist import UiGameListWidget, GAME_MAX_WIDTH, GAME_MAX_HEIGHT
from uirunninggame import UiGameIsRunningWidget
from uiwidgets import DynamicTypes, UiApp


class LutrisUiApp(UiApp):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Lutris-UI")
        if "--fullscreen" in sys.argv or "-f" in sys.argv:
            pygame.display.set_mode(flags=pygame.FULLSCREEN + pygame.RESIZABLE)
        else:
            pygame.display.set_mode((1280, 720), flags=pygame.RESIZABLE)
        super().__init__()
        self.bg_color = pygame.Color(255, 255, 255)

        ldb = LutrisDb()
        self.games_viewport = UiGameListWidget(self, ldb, size_w=-10, size_h=-10,
                                               pos_x_type=DynamicTypes.TYPE_CENTER, pos_y_type=DynamicTypes.TYPE_CENTER)
        self.game_is_running = UiGameIsRunningWidget(self, ldb, pos_x_type=DynamicTypes.TYPE_CENTER,
                                                     pos_y_type=DynamicTypes.TYPE_CENTER,
                                                     size_w=GAME_MAX_WIDTH, size_h=GAME_MAX_HEIGHT + 60)
