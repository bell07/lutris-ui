import pygame

import controls
from lutrisdb import LutrisDb
from uiwidgets import *

GAME_MAX_WIDTH = 240  # Todo: Setting
GAME_MAX_HEIGHT = GAME_MAX_WIDTH * 1.4
GAME_BORDER_WIDTH = 10  # ToDo: Setting
GAME_BORDER_HEIGHT = 10  # ToDo: Setting
TEXT_AREA_HEIGHT = 65  # ToDo: Setting


class UiGameLabel(UiWidgetTextBlock):
    def compose(self, surface: pygame.Surface) -> None:
        surface.set_alpha(128)
        super().compose(surface)


class UiGameWidget(UiWidgetStatic):
    def __init__(self, parent: UiWidget, game_data: dict, **kwargs):
        super().__init__(parent, **kwargs)
        self.set_size(size_w=GAME_MAX_WIDTH, size_h=GAME_MAX_HEIGHT)
        self.name = game_data["name"]
        self.data = game_data
        self.label_widget = UiGameLabel(parent=self, bg_color=pygame.Color(255, 255, 255),
                                        pos_x_type=DynamicTypes.TYPE_CENTER, pos_y=-GAME_BORDER_WIDTH / 2,
                                        size_w=GAME_MAX_WIDTH - GAME_BORDER_WIDTH, size_h=TEXT_AREA_HEIGHT)

    def compose(self, surface: pygame.Surface) -> None:
        max_w = GAME_MAX_WIDTH - GAME_BORDER_WIDTH
        max_h = GAME_MAX_HEIGHT - GAME_BORDER_HEIGHT

        if self.is_focus is True:
            surface.fill((128, 128, 255))
        else:
            surface.fill((255, 255, 255))

        if self.data.get("coverart") is None:
            pygame.draw.rect(surface, (128, 255, 255), (GAME_BORDER_WIDTH / 2, GAME_BORDER_HEIGHT / 2, max_w, max_h))

        else:
            img = pygame.image.load(self.data.get("coverart"))
            orig_h = img.get_height()
            orig_w = img.get_width()

            # Print Image
            if orig_h > orig_w * 1.4:
                zoom_factor = max_h / orig_h
            else:
                zoom_factor = max_w / orig_w

            resized = pygame.transform.scale_by(img, zoom_factor)
            img_pos_x = (max_w - resized.get_width()) / 2 + GAME_BORDER_WIDTH / 2
            img_pos_y = (max_h - resized.get_height()) / 2 + GAME_BORDER_HEIGHT / 2
            surface.blit(resized, (img_pos_x, img_pos_y))

        if self.label_widget.text != self.name:
            self.label_widget.text = self.name
            self.label_widget.set_changed()

    def launch(self) -> None:
        self.parent_widget.ldb.launch(self.data)
        # Game -> Viewport
        self.parent_widget.set_interactive(False)
        # Game -> Viewport -> App
        self.parent_widget.parent_widget.game_is_running.set_running(self)

    def process_events(self, events: list, pos: (int, int) = None) -> None:
        if pos is not None:
            for e in events:
                if e.type == pygame.MOUSEBUTTONUP and e.button == pygame.BUTTON_LEFT:
                    if e.touch is False:
                        self.launch()
                    else:
                        if self.is_focus is True:
                            self.launch()
                        else:
                            self.set_focus()
                    return

    def set_focus(self, focus: bool = True) -> None:
        super().set_focus(focus)


class UiGameListWidget(UiWidgetViewport):
    def __init__(self, parent: UiWidget, ldb: LutrisDb, **kwargs):
        super().__init__(parent, **kwargs)
        self.bg_color = pygame.Color(200, 200, 200)
        self.ldb = ldb
        self.max_games_cols = 0
        self.game_widgets = []
        self.set_focus()  # Initial focus for keys processing

    def get_game_position(self, index: int) -> (int, int):
        col = (index - 1) % self.max_games_cols
        row = int((index - 1) / self.max_games_cols)
        pos_x = col * (GAME_MAX_WIDTH + GAME_BORDER_WIDTH)
        pos_y = row * (GAME_MAX_HEIGHT + GAME_BORDER_HEIGHT)
        return pos_x, pos_y

    def update_games_list(self, force: bool = False) -> None:
        (visible_width, visible_height) = self.get_rect().size
        new_max_games_cols = int(visible_width / (GAME_MAX_WIDTH + GAME_BORDER_WIDTH))
        if new_max_games_cols == 0:
            new_max_games_cols = 1

        if new_max_games_cols != self.max_games_cols or force is True:
            update_widgets = True
        else:
            update_widgets = False

        self.max_games_cols = new_max_games_cols

        games_data = self.ldb.games_data
        viewport_height = (int((len(games_data) - 1) / self.max_games_cols) + 1) * (
                GAME_MAX_HEIGHT + GAME_BORDER_HEIGHT)
        if viewport_height < visible_height:
            viewport_height = visible_height
        viewport_width = visible_width
        if viewport_width < GAME_MAX_HEIGHT + GAME_BORDER_HEIGHT:
            viewport_width = GAME_MAX_HEIGHT + GAME_BORDER_HEIGHT

        self.set_viewport_size(viewport_width, viewport_height)

        if len(self.game_widgets) == 0:
            for idx, game_data in enumerate(games_data):
                pos_x, pos_y = self.get_game_position(idx + 1)
                self.game_widgets.append(UiGameWidget(self, game_data, pos_x=pos_x, pos_y=pos_y))
        elif update_widgets is True:
            for idx, widget in enumerate(self.game_widgets):
                pos_x, pos_y = self.get_game_position(idx + 1)
                widget.set_pos(pos_x=pos_x, pos_y=pos_y)
                widget.set_changed()

    def select_game(self, command: str) -> None:
        if command == "ENTER" and isinstance(self.focus_child, UiGameWidget):
            self.focus_child.launch()
            return

        selected_game_index = 0
        if self.focus_child is not None:
            for idx, game in enumerate(self.game_widgets):
                if game == self.focus_child:
                    selected_game_index = idx
                    break

        match command:
            case "UP":
                selected_game_index = selected_game_index - self.max_games_cols
            case "DOWN":
                selected_game_index = selected_game_index + self.max_games_cols
            case "LEFT":
                selected_game_index = selected_game_index - 1
            case "RIGHT":
                selected_game_index = selected_game_index + 1
            case _:
                for idx, widget in enumerate(self.game_widgets):
                    if widget.name == command:
                        selected_game_index = idx
                        break

        if selected_game_index < 0:
            selected_game_index = 0
        if len(self.game_widgets) <= selected_game_index:
            selected_game_index = len(self.game_widgets) - 1

        # Select new
        selected_widget = self.game_widgets[selected_game_index]
        selected_widget.set_focus()

        viewport_h = self.get_rect().height
        widget_rect = selected_widget.get_rect()
        if widget_rect.y < self.shift_y:
            self.shift_y = widget_rect.y

        if widget_rect.y + widget_rect.h > self.shift_y + viewport_h:
            self.shift_y = widget_rect.y + widget_rect.h - viewport_h

    def process_events(self, events: list, pos: (int, int) = None) -> None:
        super().process_events(events, pos)

        # Scroll after other events processed
        for e in events:
            match e.type:
                case controls.COMMAND_EVENT:
                    self.select_game(e.command)
                case pygame.MOUSEWHEEL:
                    self.shift_y = self.shift_y - (e.y * GAME_MAX_HEIGHT / 4)
                    self.set_changed()

    def draw(self, force: bool = False, draw_to_parent: bool = True) -> bool:
        if force is True:
            self.set_changed()
        if self.is_changed():
            self.update_games_list(force)
        return super().draw(force, draw_to_parent)
