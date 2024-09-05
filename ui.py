import pygame

GAME_MAX_WIDTH = 200  # Todo: Setting
GAME_MAX_HEIGHT = GAME_MAX_WIDTH * 1.4
GAME_BORDER_WIDTH = 20  # ToDo: Setting
GAME_BORDER_HEIGHT = 20  # ToDo: Setting

from lutrisdb import LutrisDb

from uiwidgets import UiWidgetsContainer, UiWidgetInteractive, UiWidgetsViewport


class UiGameWidget(UiWidgetInteractive):
    def __init__(self, surface, x, y, w, h, game_data):
        super().__init__(surface, x, y, w, h)
        self._coverart = game_data.get("coverart")
        self.name = game_data["name"]

    def blit_text(self, surface, text, pos, font, color=pygame.Color('black')):
        words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
        space = font.size(' ')[0]  # The width of a space.
        max_width, max_height = surface.get_size()
        x, y = pos
        for line in words:
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
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.

    def compose(self):
        if self._coverart is None:
            self.widget_surface.fill((128, 255, 255))

        else:
            img = pygame.image.load(self._coverart)
            orig_h = img.get_height()
            orig_w = img.get_width()

            max_w = GAME_MAX_WIDTH
            max_h = GAME_MAX_HEIGHT

            # Print Image
            if orig_h > orig_w * 1.4:
                zoom_factor = max_h / orig_h
            else:
                zoom_factor = max_w / orig_w

            resized = pygame.transform.scale_by(img, zoom_factor)
            img_pos_x = (max_w - resized.get_width()) / 2
            img_pos_y = (max_h - resized.get_height()) / 2
            self.widget_surface.blit(resized, (img_pos_x, img_pos_y))

        # Print Name
        self.blit_text(self.widget_surface, self.name, (GAME_BORDER_WIDTH / 2, GAME_BORDER_HEIGHT / 2),
                       pygame.font.SysFont(None, 30))


class UiGameListWidget(UiWidgetsViewport, UiWidgetsContainer):
    def __init__(self, surface, x, y, w, h):
        self._ldb = LutrisDb()
        self.max_games_cols = 0
        super().__init__(surface, x, y, w, h)

    def init_games(self):
        games_data = self._ldb.games_data
        viewport_height = (int((len(games_data) - 1) / self.max_games_cols) + 1) * (
                GAME_MAX_HEIGHT + GAME_BORDER_HEIGHT)
        if viewport_height < self.h:
            viewport_height = self.h
        viewport_width = self.w
        if viewport_width < GAME_MAX_HEIGHT + GAME_BORDER_HEIGHT:
            viewport_width = GAME_MAX_HEIGHT + GAME_BORDER_HEIGHT

        self.set_viewport_size(viewport_width, viewport_height)

        index = 0
        self.widgets = []
        for game_data in games_data:
            index = index + 1
            pos_x, pos_y = self.get_game_position(index)

            self.add_widget(
                UiGameWidget(self.viewport_surface, pos_x, pos_y, GAME_MAX_WIDTH, GAME_MAX_HEIGHT, game_data))
        UiWidgetsContainer.compose(self)

    def adjust_dimensions(self):
        super().adjust_dimensions()
        self.max_games_cols = int(self.w / (GAME_MAX_WIDTH + GAME_BORDER_WIDTH))
        if self.max_games_cols == 0:
            self.max_games_cols = 1
        self.init_games()

    def set_background(self):
        self.viewport_surface.fill((255, 255, 255))

    def get_game_position(self, index):
        col = (index - 1) % self.max_games_cols
        row = int((index - 1) / self.max_games_cols)
        pos_x = col * (GAME_MAX_WIDTH + GAME_BORDER_WIDTH) + GAME_BORDER_WIDTH / 2
        pos_y = row * (GAME_MAX_HEIGHT + GAME_BORDER_HEIGHT) + GAME_BORDER_HEIGHT / 2
        return pos_x, pos_y


class UiScreen(UiWidgetsContainer):
    def __init__(self, surface, x, y, w, h):
        super().__init__(surface, x, y, w, h)
        self.add_widget(UiGameListWidget(self.widget_surface, 10, 10, -10, -10))

    def set_background(self):
        self.widget_surface.fill((255, 255, 255))

    def process_events(self, events):
        for e in events:
            match e.type:
                case pygame.VIDEORESIZE:
                    self.adjust_dimensions()
                    self.draw(True)

    def compose(self):
        super().compose()
        pygame.display.flip()


class Ui:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Lutris-UI")
        self._screen = pygame.display.set_mode((1280, 720), flags=pygame.RESIZABLE)
        # self._screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
        self._clock = pygame.time.Clock()
        self.screen_widget = UiScreen(self._screen, 0, 0, 0, 0)

    def draw(self):
        # Fill the background with white
        self.screen_widget.draw()

        self._clock.tick(30)  # limits FPS to 30

    def process_controls(self, ctr):
        key = ctr.get_pressed_key()
        if key is not None:
            print(f"Pressed key: {key}")

        self.screen_widget.process_events(ctr.events)
