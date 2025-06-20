from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pygame import Color, constants
from uigamelist import GAME_WIDGET_HEIGHT, GAME_WIDGET_WIDTH, UiGameWidget
from uiwidgets import (Controls, DynamicTypes, UiWidget, UiWidgetStatic,
                       UiWidgetTextBlock)

if TYPE_CHECKING:
    from lutrisuiapp import LutrisUiApp
    from pygame import event


class UiRunningGameWidget(UiGameWidget):
    def process_event_focus(self, event: event.Event) -> bool:
        return False

    def process_event_pos(self, event: event.Event, pos: tuple[int, int]):
        return False

    def set_focus(self, focus: bool = True) -> None:
        pass


class UiTerminateGame(UiWidgetTextBlock):
    def process_event_pos(self, event: event.Event, pos: tuple[int, int]) -> bool:
        if (
            event.type == constants.MOUSEBUTTONUP
            and event.button == constants.BUTTON_LEFT
        ):
            cast(
                "LutrisUiApp", self.get_root_widget()
            ).game_is_running.set_kill_running()
            return True
        return False

    def process_event_focus(self, event: event.Event) -> bool:
        if event.type == Controls.COMMAND_EVENT and (
            event.command == "BACK" or event.command == "EXIT"
        ):
            cast(
                "LutrisUiApp", self.get_root_widget()
            ).game_is_running.set_kill_running()
            return True
        return False


class UiGameIsRunningWidget(UiWidget):
    def __init__(self, parent: UiWidget, **kwargs):
        super().__init__(parent, **kwargs)
        self.ldb = cast("LutrisUiApp", self.get_root_widget()).ldb
        self.is_visible = False
        self.game_data = None
        UiWidgetStatic(self, alpha=200, bg_color="Grey")  # Fog
        popup = UiWidget(
            self,
            pos_x_type=DynamicTypes.TYPE_CENTER,
            pos_y_type=DynamicTypes.TYPE_CENTER,
        )
        self.game_widget = UiRunningGameWidget(
            popup, pos_x_type=DynamicTypes.TYPE_CENTER
        )
        button_size = 100
        self.button = UiTerminateGame(
            popup,
            pos_x_type=DynamicTypes.TYPE_CENTER,
            pos_y_type=DynamicTypes.TYPE_PIXEL_REVERSE,
            size_h=button_size,
            border_color=self.game_widget.border_color,
            border_all=10,
            border_top=0,
            text_centered_x=True,
            text_centered_y=True,
        )
        popup.set_size(
            size_w=GAME_WIDGET_WIDTH, size_h=GAME_WIDGET_HEIGHT + button_size
        )
        self._kill_in_progress = False

    def set_kill_running(self):
        if self._kill_in_progress is False:
            self._kill_in_progress = True
            self.button.text = "Terminating ..."
            self.button.bg_color = Color("Yellow")
            self.button.set_changed()

    def set_running(self, game_data) -> None:
        self.game_data = game_data
        self._kill_in_progress = False

        self.set_visible()
        self.set_focus()

        self.button.text = "Cancel"
        self.button.bg_color = Color("Red")
        self.button.set_focus()
        self.button.set_changed()

        self.game_widget.name = game_data["name"]
        self.game_widget.data = game_data
        self.game_widget.set_changed()
        self.set_process_tick_enabled()

    def process_tick(self) -> None:
        if self.game_data is None:
            return

        if self.ldb.check_is_running(self._kill_in_progress) is False:
            self.game_data = None
            cast("LutrisUiApp", self.get_root_widget()).launch_completed()
            self.set_process_tick_enabled(False)
        else:
            if self._kill_in_progress is True:
                self.ldb.kill_running()
