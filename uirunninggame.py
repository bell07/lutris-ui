import pygame

from settings import Settings
from uigamelist import UiGameWidget
from uiwidgets import UiWidget, UiWidgetStatic, DynamicTypes, UiWidgetTextBlock, Controls


class UiRunningGameWidget(UiGameWidget):
    def process_events(self, events: list, pos: (int, int) = None) -> None:
        pass

    def set_focus(self, focus: bool = True) -> None:
        pass


class UiTerminateGame(UiWidgetTextBlock):
    def process_events(self, events: list, pos: (int, int) = None) -> None:
        for e in events:
            match e.type:
                case pygame.MOUSEBUTTONUP:
                    if e.button == pygame.BUTTON_LEFT:
                        self.parent_widget.parent_widget.set_kill_running()
                        return
                case Controls.COMMAND_EVENT:
                    if e.command == "ENTER" or e.command == "EXIT":
                        self.parent_widget.parent_widget.set_kill_running()
                        return


class UiGameIsRunningWidget(UiWidget):
    def __init__(self, parent: UiWidget, **kwargs):
        super().__init__(parent, **kwargs)
        self.ldb = self.get_root_widget().ldb
        self.is_visible = False
        self.game_data = None
        UiWidgetStatic(self, alpha=200, bg_color="Grey")  # Fog
        popup = UiWidget(self, pos_x_type=DynamicTypes.TYPE_CENTER, pos_y_type=DynamicTypes.TYPE_CENTER)
        self.game_widget = UiRunningGameWidget(popup, pos_x_type=DynamicTypes.TYPE_CENTER)
        button_size = 100
        self.button = UiTerminateGame(popup, size_h=button_size, pos_x_type=DynamicTypes.TYPE_CENTER, pos_y=-0.1,
                                      border_color=self.game_widget.border_color, border_all=10, border_top=0,
                                      text_centered_x=True, text_centered_y=True)
        gw_rect = self.game_widget.get_rect(with_borders=True)
        popup.set_size(size_w=gw_rect.w, size_h=gw_rect.h + button_size)

        self._hide_on_launch = Settings("play").get("hide_on_launch", False)
        self._kill_in_progress = False

    def set_kill_running(self):
        if self._kill_in_progress is False:
            self._kill_in_progress = True
            self.button.text = "Terminating ..."
            self.button.bg_color = "Yellow"
            self.button.set_changed()

    def set_running(self, game_data) -> None:
        self.game_data = game_data
        self._kill_in_progress = False

        self.parent_widget.games_viewport.set_interactive(False)
        self.set_visible()
        self.set_focus()

        self.button.text = "Cancel"
        self.button.bg_color = "Red"
        self.button.set_focus()
        self.button.set_changed()

        self.game_widget.name = game_data["name"]
        self.game_widget.data = game_data
        self.game_widget.set_changed()
        if self._hide_on_launch is True:
            pygame.display.iconify()

    def process_tick(self, milliseconds: int) -> None:
        if self.game_data is None:
            return

        if self.ldb.check_is_running() is False:
            self.ldb.data_changed = True
            self.set_visible(False)
            self.game_data = None
            if self._hide_on_launch is True:
                self.parent_widget.init_display_settings()

            self.parent_widget.games_viewport.set_focus(True)
        else:
            if self._kill_in_progress is True:
                self.ldb.kill_running()
            pygame.time.wait(270)
