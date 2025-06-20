from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pygame import Color, constants, draw, event, image, transform
from settings import Settings
from uiwidgets import (Controls, DynamicTypes, UiWidgetStatic,
                       UiWidgetTextBlock, UiWidgetViewport,
                       UiWidgetViewportContainer)

if TYPE_CHECKING:
    from lutrisuiapp import LutrisUiApp
    from pygame import Surface
    from uiwidgets import UiWidget


game_list_settings = Settings("game_widget")
GAME_WIDGET_WIDTH: int = game_list_settings.get("width", 240)
GAME_WIDGET_HEIGHT = int(GAME_WIDGET_WIDTH * 1.4)
GAME_DISTANCE_WIDTH: int = game_list_settings.get("distance_width", 10)
GAME_DISTANCE_HEIGHT: int = game_list_settings.get("distance_height", 10)
TEXT_AREA_HEIGHT: int = game_list_settings.get("label_height", 65)


class UiGameWidget(UiWidgetStatic):
    def __init__(self, parent: UiWidget, game_data: dict | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.set_size(size_w=GAME_WIDGET_WIDTH, size_h=GAME_WIDGET_HEIGHT)
        self.set_border(border_all=10, border_color=Color("White"))
        self.name: str
        self.data: dict
        if game_data:
            self.name: str = game_data["name"]
            self.data: dict = game_data
        self.label_widget = UiWidgetTextBlock(
            parent=self,
            bg_color=Color(255, 255, 255, 100),
            text_color=Color(50, 50, 50),
            surface_flags=constants.SRCALPHA,
            text_centered_x=True,
            text_centered_y=True,
            pos_x_type=DynamicTypes.TYPE_CENTER,
            pos_y_type=DynamicTypes.TYPE_PIXEL_REVERSE,
            size_h=TEXT_AREA_HEIGHT,
        )

    def compose(self, surface: Surface) -> None:
        assert self.data
        max_w = surface.get_width()
        max_h = surface.get_height()

        if self.is_focus is True:
            surface.fill((128, 128, 255))
        else:
            surface.fill((255, 255, 255))

        coverart = self.data.get("coverart")
        if coverart is None:
            draw.rect(surface, (128, 255, 255), (0, 0, max_w, max_h))
        else:
            img = image.load(coverart)
            orig_h = img.get_height()
            orig_w = img.get_width()

            # Print Image
            if orig_h > orig_w * 1.4:
                zoom_factor = max_h / orig_h
            else:
                zoom_factor = max_w / orig_w

            resized = transform.scale_by(img, zoom_factor)
            img_pos_x = (max_w - resized.get_width()) / 2
            img_pos_y = (max_h - resized.get_height()) / 2
            surface.blit(resized, (img_pos_x, img_pos_y))

        if self.label_widget.text != self.name:
            self.label_widget.text = self.name
            self.label_widget.set_changed()

    def process_event_focus(self, event: event.Event) -> bool:
        app = self.get_root_widget()
        if event.type == Controls.COMMAND_EVENT and event.command == "ENTER":
            cast("LutrisUiApp", app).launch(self.data)
            return True
        return False

    def process_event_pos(self, event: event.Event, pos: tuple[int, int]) -> bool:
        app = self.get_root_widget()
        if (
            event.type == constants.MOUSEBUTTONUP
            and event.button == constants.BUTTON_LEFT
        ):
            if event.touch is False:
                cast("LutrisUiApp", app).launch(self.data)
            else:
                if self.is_focus is True:
                    cast("LutrisUiApp", app).launch(self.data)
                else:
                    self.set_focus()
            return True
        return False

    def set_focus(self, focus: bool = True) -> None:
        if focus == self.is_focus:
            return
        super().set_focus(focus)
        if focus is True:
            self.set_border(border_color=Color(128, 128, 255), border_all=5)
        else:
            self.set_border(border_color=Color("White"), border_all=10)
        self.set_changed()


class UiGameViewport(UiWidgetViewport):
    def __init__(self, parent: UiWidget, **kwargs):
        super().__init__(parent, **kwargs)
        self.max_games_cols = 0
        self.game_widgets = []
        app = self.get_root_widget()
        self.ldb = cast("LutrisUiApp", app).ldb
        self._old_width = 0

    def get_game_position(self, index: int, optimized_width: int) -> tuple[int, int]:
        col = (index - 1) % self.max_games_cols
        row = int((index - 1) / self.max_games_cols)
        pos_x = col * (GAME_WIDGET_WIDTH + optimized_width)
        pos_y = row * (GAME_WIDGET_HEIGHT + GAME_DISTANCE_HEIGHT)
        return pos_x, pos_y

    def update_games_list(self) -> None:
        (visible_width, visible_height) = self.get_parent_size()

        if self._old_width != visible_width:
            self._old_width = visible_width
            update_widgets = True
            self.max_games_cols = int(
                visible_width / (GAME_WIDGET_WIDTH + GAME_DISTANCE_WIDTH)
            )
            if self.max_games_cols == 0:
                self.max_games_cols = 1
        else:
            update_widgets = False

        games_data, list_updated = self.ldb.get_games()
        viewport_height = (int((len(games_data) - 1) / self.max_games_cols) + 1) * (
            GAME_WIDGET_HEIGHT + GAME_DISTANCE_HEIGHT
        )

        self.set_size(size_w=GAME_WIDGET_WIDTH, size_h=viewport_height)

        if self.max_games_cols >= len(games_data):
            optimized_distance_width = GAME_DISTANCE_WIDTH
        else:
            optimized_distance_width = round(
                (visible_width - self.max_games_cols * GAME_WIDGET_WIDTH)
                / self.max_games_cols
            )

        if not self.game_widgets:
            for idx, game_data in enumerate(games_data):
                pos_x, pos_y = self.get_game_position(idx + 1, optimized_distance_width)
                self.game_widgets.append(
                    UiGameWidget(self, game_data, pos_x=pos_x, pos_y=pos_y)
                )
            self.select_game("TOP")
        elif update_widgets is True or list_updated is True:
            for idx, game_data in enumerate(games_data):
                pos_x, pos_y = self.get_game_position(idx + 1, optimized_distance_width)
                widget_found = False
                if idx < len(self.game_widgets):
                    for old_idx in range(idx, len(self.game_widgets)):
                        widget = self.game_widgets[old_idx]
                        if widget.name == game_data["name"]:
                            widget.set_pos(pos_x=pos_x, pos_y=pos_y)
                            widget.set_changed()
                            widget_found = True
                            self.game_widgets.insert(
                                idx, self.game_widgets.pop(old_idx)
                            )
                            break
                if widget_found is False:
                    self.game_widgets.insert(
                        idx, UiGameWidget(self, game_data, pos_x=pos_x, pos_y=pos_y)
                    )
            if len(games_data) < len(self.game_widgets):
                for old_idx in range(len(games_data), len(self.game_widgets)):
                    widget = self.game_widgets[old_idx]
                    self.remove_child(widget)
                    self.game_widgets.pop(old_idx)

    def select_game(self, command: str) -> bool:
        selected_game_index = 0
        if self.focus_child:
            selected_game_index = self.game_widgets.index(self.focus_child)

        match command:
            case "TOP":
                selected_game_index = 0
            case "UP":
                selected_game_index -= self.max_games_cols
            case "DOWN":
                selected_game_index += self.max_games_cols
            case "BOTTOM":
                selected_game_index = len(self.game_widgets) - 1
            case "LEFT":
                selected_game_index -= 1
            case "RIGHT":
                selected_game_index += 1
            case "RELOAD":
                self.ldb.data_changed = True
                self.set_changed()
            case _:
                return False

        if selected_game_index < 0:
            selected_game_index = 0
        if len(self.game_widgets) <= selected_game_index:
            selected_game_index = len(self.game_widgets) - 1

        # Select new
        selected_widget = self.game_widgets[selected_game_index]
        selected_widget.set_focus()

        assert self.parent_widget
        viewport_h = self.parent_widget.get_rect(with_borders=False).height
        widget_rect = selected_widget.get_rect(with_borders=True)
        if widget_rect.y < self.shift_y:
            self.shift_y = widget_rect.y

        if widget_rect.y + widget_rect.h > self.shift_y + viewport_h:
            self.shift_y = widget_rect.y + widget_rect.h - viewport_h

        return True

    def process_event_focus(self, event: event.Event) -> bool:
        match event.type:
            case Controls.COMMAND_EVENT:
                if self.select_game(event.command) is True:
                    return True
            case constants.MOUSEWHEEL:
                self.shift_y = self.shift_y - (event.y * GAME_WIDGET_HEIGHT / 4)
                self.set_changed()
                return True
        return super().process_event_focus(event)

    def draw(self) -> None:
        if self.is_changed() or self.is_parent_changed():
            self.update_games_list()
        return super().draw()


class UiGameListWidget(UiWidgetViewportContainer):
    def __init__(self, parent: UiWidget, **kwargs):
        super().__init__(parent, **kwargs)
        self.bg_color = "Grey"
        self.set_viewport_widget(UiGameViewport(parent=self, bg_color=self.bg_color))
