import pygame

from uiwidgets import UiWidgetStatic, UiWidget


class UiWidgetTextBlock(UiWidgetStatic):

    def __init__(self, parent: UiWidget, text: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        self.text = text
        self.color = pygame.Color('black')
        self.font = pygame.font.SysFont(None, 30)

    def compose(self, surface: pygame.Surface) -> None:
        words = [word.split(' ') for word in self.text.splitlines()]  # 2D array where each row is a list of words.
        space = self.font.size(' ')[0]  # The width of a space.
        (max_width, max_height) = surface.get_size()
        x, y = 0, 0
        for line in words:
            line_height = 0
            for word in line:
                word_surface = self.font.render(word, 0, self.color)
                (word_width, word_height) = word_surface.get_size()
                if x + word_width >= max_width:
                    x = 0
                    y += word_height  # Start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
                if word_height > line_height:
                    line_height = word_height
            x = 0
            y += line_height
