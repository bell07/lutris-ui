import pygame

import controls
from lutrisdb import LutrisDb
from uigamelist import UiGameWidget
from uiwidgets import UiWidget, DynamicTypes, UiWidgetTextBlock


class UiRunningGameWidget(UiGameWidget):
    def process_events(self, events: list, pos: (int, int) = None) -> None:
        pass

    def set_focus(self, focus: bool = True) -> None:
        super().set_focus(False)


class UiTerminateGame(UiWidgetTextBlock):
    def __init__(self, parent: UiWidget, label: str, **kwargs) -> None:
        super().__init__(parent=parent, text=label, **kwargs)
        self.bg_color = pygame.Color(200, 200, 200)

    def process_events(self, events: list, pos: (int, int) = None) -> None:
        for e in events:
            match e.type:
                case pygame.MOUSEBUTTONUP:
                    if e.button == pygame.BUTTON_LEFT:
                        self.parent_widget.ldb.kill_running()
                        return
                case controls.COMMAND_EVENT:
                    if e.command == "ENTER" or e.command == "EXIT":
                        self.parent_widget.ldb.kill_running()
                        return


class UiGameIsRunningWidget(UiWidget):
    def __init__(self, parent: UiWidget, ldb: LutrisDb, **kwargs):
        self.ldb = ldb
        super().__init__(parent, **kwargs)
        self.bg_color = pygame.Color(255, 255, 255)
        self.is_visible = False
        self.game = None
        self.game_widget = None
        self.button = UiTerminateGame(self, "Terminate", size_h=60, pos_x_type=DynamicTypes.TYPE_CENTER, pos_y=-1)

    def set_running(self, game: UiGameWidget) -> None:
        self.game = game
        self.set_visible()
        self.button.set_focus()
        self.parent_widget.set_changed()
        if self.game_widget is None:
            self.game_widget = UiRunningGameWidget(self, game.data, pos_x_type=DynamicTypes.TYPE_CENTER)
        else:
            self.game_widget.name = game.name
            self.game_widget.data = game.data
            self.game_widget.set_changed()

    def process_tick(self, milliseconds: int) -> None:
        if self.game is None:
            return

        if self.ldb.check_is_running() is False:
            self.parent_widget.games_viewport.set_interactive()
            self.parent_widget.games_viewport.set_focus()
            self.set_visible(False)
            self.game = None
            self.parent_widget.set_changed()
        else:
            pygame.time.wait(970)
