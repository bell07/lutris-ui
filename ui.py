import pygame

from lutrisdb import LutrisDb
from uiwidgets import UiWidget, UiWidgetsViewport, UiWidgetStatic

GAME_MAX_WIDTH = 200  # Todo: Setting
GAME_MAX_HEIGHT = GAME_MAX_WIDTH * 1.4
GAME_BORDER_WIDTH = 10  # ToDo: Setting
GAME_BORDER_HEIGHT = 10  # ToDo: Setting


class UiGameWidget(UiWidgetStatic):
    def __init__(self, parent, x, y, w, h, game_data):
        super().__init__(parent, x, y, w, h)
        self._coverart = game_data.get("coverart")
        self.name = game_data["name"]

    @staticmethod
    def blit_text(surface, text, pos, font, color=pygame.Color('black')):
        words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
        space = font.size(' ')[0]  # The width of a space.
        max_width, max_height = surface.get_size()
        x, y = pos
        for line in words:
            line_height = 0
            for word in line:
                word_surface = font.render(word, 0, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                word_bg_surface = pygame.Surface((word_width, word_height))
                word_bg_surface.fill(pygame.Color(255, 255, 255))
                word_bg_surface.set_alpha(10)
                surface.blit(word_bg_surface, (x, y))
                surface.blit(word_surface, (x, y))
                x += word_width + space
                if word_height > line_height:
                    line_height = word_height
            x = pos[0]  # Reset the x.
            y += line_height  # Start on new row.

    def compose(self, surface):
        max_w = GAME_MAX_WIDTH - GAME_BORDER_WIDTH
        max_h = GAME_MAX_HEIGHT - GAME_BORDER_HEIGHT

        if self.is_focus is True:
            surface.fill((128, 128, 255))
        else:
            surface.fill((255, 255, 255))

        if self._coverart is None:
            pygame.draw.rect(surface, (128, 255, 255), (
                GAME_BORDER_WIDTH / 2, GAME_BORDER_HEIGHT / 2, max_w - GAME_BORDER_WIDTH / 2,
                max_h - GAME_BORDER_HEIGHT / 2))

        else:
            img = pygame.image.load(self._coverart)
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

        # Print Name
        self.blit_text(surface.subsurface((GAME_BORDER_WIDTH / 2, GAME_BORDER_HEIGHT / 2, max_w - GAME_BORDER_WIDTH / 2,
                                           max_h - GAME_BORDER_HEIGHT / 2)), self.name, (0, 0),
                       pygame.font.SysFont(None, 30))


class UiGameListWidget(UiWidgetsViewport):
    def __init__(self, parent, x, y, w, h):
        super().__init__(parent, x, y, w, h)
        self._ldb = LutrisDb()
        self.max_games_cols = 0
        self.game_widgets = []
        self.update_games_list()
        self.set_vertical_scrollbar()

    def compose(self, surface):
        surface.fill((200, 200, 200))

    def get_game_position(self, index):
        col = (index - 1) % self.max_games_cols
        row = int((index - 1) / self.max_games_cols)
        pos_x = col * (GAME_MAX_WIDTH + GAME_BORDER_WIDTH)
        pos_y = row * (GAME_MAX_HEIGHT + GAME_BORDER_HEIGHT)
        return pos_x, pos_y

    def update_games_list(self, force=False):
        x, y, w, h = self.get_widget_dimensions(self.get_parent_surface())
        mew_max_games_cols = int(w / (GAME_MAX_WIDTH + GAME_BORDER_WIDTH))
        if mew_max_games_cols == 0:
            mew_max_games_cols = 1

        if mew_max_games_cols != self.max_games_cols or force is True:
            self.max_games_cols = mew_max_games_cols

            games_data = self._ldb.games_data
            viewport_height = (int((len(games_data) - 1) / self.max_games_cols) + 1) * (
                    GAME_MAX_HEIGHT + GAME_BORDER_HEIGHT)
            if viewport_height < h:
                viewport_height = h
            viewport_width = w
            if viewport_width < GAME_MAX_HEIGHT + GAME_BORDER_HEIGHT:
                viewport_width = GAME_MAX_HEIGHT + GAME_BORDER_HEIGHT

            self.set_viewport_size(viewport_width, viewport_height)

            if len(self.game_widgets) == 0:
                for idx, game_data in enumerate(games_data):
                    pos_x, pos_y = self.get_game_position(idx + 1)
                    self.game_widgets.append(
                        UiGameWidget(self, pos_x, pos_y, GAME_MAX_WIDTH, GAME_MAX_HEIGHT, game_data))
            else:
                for idx, widget in enumerate(self.game_widgets):
                    pos_x, pos_y = self.get_game_position(idx + 1)
                    widget.def_x = pos_x
                    widget.def_y = pos_y
                    widget.set_changed()
            self.set_changed()

    def select_game(self, game_name_or_direction):
        selected_game_index = None
        for idx, widget in enumerate(self.game_widgets):
            if widget.is_focus is True:
                selected_game_index = idx

        if selected_game_index is None:
            selected_game_index = 0
        else:
            widget = self.game_widgets[selected_game_index]
            widget.is_focus = False
            widget.draw(force=True)
            widget.set_changed()

        match game_name_or_direction:
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
                    if widget.name == game_name_or_direction:
                        selected_game_index = idx

        if selected_game_index < 0:
            selected_game_index = 0
        if len(self.game_widgets) <= selected_game_index:
            selected_game_index = len(self.game_widgets) - 1

        widget = self.game_widgets[selected_game_index]
        widget.is_focus = True
        widget.draw(force=True)
        widget.set_changed()

        _, _, _, viewport_h = self.get_widget_dimensions(self.get_parent_surface())
        _, widget_y, _, widget_h = widget.get_widget_dimensions(self.get_surface())
        if widget_y < self.shift_y:
            self.shift_y = widget_y

        if widget_y + widget_h > self.shift_y + viewport_h:
            self.shift_y = widget_y + widget_h - viewport_h

        self.set_changed()

    def process_events(self, events):
        for e in events:
            match e.type:
                case pygame.KEYDOWN:
                    match e.key:
                        case pygame.K_UP:
                            self.select_game("UP")
                        case pygame.K_DOWN:
                            self.select_game("DOWN")
                        case pygame.K_LEFT:
                            self.select_game("LEFT")
                        case pygame.K_RIGHT:
                            self.select_game("RIGHT")

    def draw(self, force=False):
        if force is True or self.is_changed():
            self.update_games_list(force)
        super().draw(force)


class UiScreen(UiWidget):
    def __init__(self, parent, x, y, w, h):
        super().__init__(parent, x, y, w, h)
        self.games_viewport = UiGameListWidget(self, 5, 5, -5, -5)

    def process_events(self, events):
        for e in events:
            match e.type:
                case pygame.VIDEORESIZE:
                    self.games_viewport.viewport_width = None  # Auto adjust to maximum
                    self.games_viewport.init_widget_surface()
                    self.draw(force=True)
                case pygame.QUIT:
                    return False
        super().process_events(events)

    def compose(self, surface):
        surface.fill((255, 255, 255))

    def draw(self, force=False):
        super().draw(force)
        pygame.display.flip()


class Ui:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Lutris-UI")
        self._screen = pygame.display.set_mode((1280, 720), flags=pygame.RESIZABLE)
        # self._screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
        self.screen_widget = UiScreen(self._screen, 0, 0, 0, 0)

    def draw_ui(self):
        self.screen_widget.draw()

    def process_controls(self, ctr):
        return self.screen_widget.process_events(ctr.events)
