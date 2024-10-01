import pygame

from lutrisdb import LutrisDb
from uigamelist import UiGameListWidget, GAME_WIDGET_WIDTH, GAME_WIDGET_HEIGHT
from uirunninggame import UiGameIsRunningWidget
from uiwidgets import DynamicTypes, UiApp


class LutrisUiApp(UiApp):
    def __init__(self):
        super().__init__(bg_color=pygame.Color(255, 255, 255))
        ldb = LutrisDb()
        self.games_viewport = UiGameListWidget(self, ldb, size_w=-10, size_h=-10,
                                               pos_x_type=DynamicTypes.TYPE_CENTER, pos_y_type=DynamicTypes.TYPE_CENTER)
        self.game_is_running = UiGameIsRunningWidget(self, ldb, pos_x_type=DynamicTypes.TYPE_CENTER,
                                                     pos_y_type=DynamicTypes.TYPE_CENTER,
                                                     size_w=GAME_WIDGET_WIDTH, size_h=GAME_WIDGET_HEIGHT + 60)

    def init_display_settings(self):
        super().init_display_settings()
        pygame.display.set_caption("Lutris-UI")

    def process_events(self, events: list, pos: (int, int) = None) -> bool:
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN and e.mod == pygame.KMOD_LALT:
                pygame.display.toggle_fullscreen()
                return True
        return super().process_events(events, pos)
