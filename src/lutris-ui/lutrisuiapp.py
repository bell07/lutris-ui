import sys

import pygame

from lutrisdb import LutrisDb
from settings import Settings
from uigamelist import UiGameListWidget
from uirunninggame import UiGameIsRunningWidget
from uiwidgets import UiApp, Controls


class LutrisUiApp(UiApp):
    def __init__(self, controls: Controls):
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
        super().__init__(controls=controls, size_w=size_w, size_h=size_h, fullscreen=fullscreen, noframe=noframe)
        pygame.display.set_caption("Lutris-UI")
        icon_path = self.settings.get_ressource_path('lutris-ui.png')
        pygame.display.set_icon(pygame.image.load(icon_path))
        self.ldb = LutrisDb()
        self.games_viewport = UiGameListWidget(self, border_all=10, border_color="Grey")
        self.game_is_running = UiGameIsRunningWidget(self, border_all=10, border_color="Grey")
        self._hide_on_launch = Settings("play").get("hide_on_launch", False)

    def process_event_focus(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and event.mod == pygame.KMOD_LALT:
            self.fullscreen = not self.fullscreen
            self.init_display_settings(reset=True)
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and event.mod == pygame.KMOD_RALT:
            self.noframe = not self.noframe
            self.fullscreen = False
            self.init_display_settings(reset=True)
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP and event.mod == pygame.KMOD_LALT:
            self.init_display_settings()
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN and event.mod == pygame.KMOD_LALT:
            pygame.display.iconify()
            return True
        return super().process_event_focus(event)

    def launch(self, game_data) -> None:
        self.ldb.launch(game_data)
        self.games_viewport.set_interactive(False)
        self.game_is_running.set_running(game_data)
        if self._hide_on_launch is True:
            pygame.display.iconify()

    def launch_completed(self) -> None:
        self.ldb.data_changed = True
        self.game_is_running.set_visible(False)
        if self._hide_on_launch is True:
            self.init_display_settings()
        self.games_viewport.set_focus()
