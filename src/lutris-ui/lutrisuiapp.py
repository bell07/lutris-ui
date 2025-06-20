from __future__ import annotations

from sys import argv
from typing import TYPE_CHECKING

from lutrisdb import LutrisDb
from pygame import constants, display, event, image
from settings import Settings
from uigamelist import UiGameListWidget
from uirunninggame import UiGameIsRunningWidget
from uiwidgets import UiApp

if TYPE_CHECKING:
    from uiwidgets import Controls


class LutrisUiApp(UiApp):
    def __init__(self, controls: Controls):
        self.settings = Settings("window")

        if "--fullscreen" in argv or "-f" in argv:
            fullscreen = True
        else:
            fullscreen = self.settings.get("fullscreen", False)
        assert isinstance(fullscreen, bool)

        if "--noframe" in argv or "-n" in argv:
            noframe = True
        else:
            noframe = self.settings.get("noframe", False)
        assert isinstance(noframe, bool)

        size_w = self.settings.get("size_w", 0)
        size_h = self.settings.get("size_h", 0)
        assert isinstance(size_w, int) and isinstance(size_h, int)
        super().__init__(
            controls=controls,
            size_w=size_w,
            size_h=size_h,
            fullscreen=fullscreen,
            noframe=noframe,
        )
        display.set_caption("Lutris-UI")
        icon_path: str = self.settings.get_ressource_path("lutris-ui.png")
        display.set_icon(image.load(icon_path))
        self.ldb = LutrisDb()
        self.games_viewport = UiGameListWidget(self, border_all=10, border_color="Grey")
        self.game_is_running = UiGameIsRunningWidget(
            self, border_all=10, border_color="Grey"
        )
        self._hide_on_launch = Settings("play").get("hide_on_launch", False)
        assert isinstance(self._hide_on_launch, bool)

    def process_event_focus(self, event: event.Event) -> bool:
        if (
            event.type == constants.KEYDOWN
            and event.key == constants.K_RETURN
            and event.mod == constants.KMOD_LALT
        ):
            self.fullscreen = not self.fullscreen
            self.init_display_settings(reset=True)
            return True
        if (
            event.type == constants.KEYDOWN
            and event.key == constants.K_RETURN
            and event.mod == constants.KMOD_RALT
        ):
            self.noframe = not self.noframe
            self.fullscreen = False
            self.init_display_settings(reset=True)
            return True
        if (
            event.type == constants.KEYDOWN
            and event.key == constants.K_UP
            and event.mod == constants.KMOD_LALT
        ):
            self.init_display_settings()
            return True
        if (
            event.type == constants.KEYDOWN
            and event.key == constants.K_DOWN
            and event.mod == constants.KMOD_LALT
        ):
            display.iconify()
            return True
        return super().process_event_focus(event)

    def launch(self, game_data) -> None:
        self.ldb.launch(game_data)
        self.games_viewport.set_interactive(False)
        self.game_is_running.set_running(game_data)
        if self._hide_on_launch is True:
            display.iconify()

    def launch_completed(self) -> None:
        self.ldb.data_changed = True
        self.game_is_running.set_visible(False)
        if self._hide_on_launch is True:
            self.init_display_settings()
        self.games_viewport.set_focus()
