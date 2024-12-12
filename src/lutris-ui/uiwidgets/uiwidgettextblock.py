from pygame import Color, font, Surface

from uiwidgets import UiWidgetStatic, UiWidget


class UiWidgetTextBlock(UiWidgetStatic):
    def __init__(self, parent: UiWidget, text: str = None, text_color: Color = None,
                 text_font: font.Font = None,
                 text_centered_x: bool = False, text_centered_y: bool = False,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.text = text or ""
        self.text_color = text_color or Color('black')
        self.text_font = text_font or font.SysFont(None, 30)
        self.text_centered_x = text_centered_x
        self.text_centered_y = text_centered_y

    def compose(self, surface: Surface) -> None:
        words = [word.split(' ') for word in self.text.splitlines()]  # 2D array where each row is a list of words.
        space = self.text_font.size(' ')[0]  # The width of a space.
        (surface_max_width, surface_max_height) = surface.get_size()
        text_map = []
        x, y = 0, 0
        line_max_width, all_lines_max_height = 0, 0
        current_line = []
        for line in words:
            line_height = 0
            for word in line:
                word_surface = self.text_font.render(word, 0, self.text_color)
                (word_width, word_height) = word_surface.get_size()
                if x + word_width >= surface_max_width:
                    text_map.append([current_line, x - space])
                    x = 0
                    y += line_height  # Start on new row.
                    current_line = []
                    all_lines_max_height += line_height

                current_line.append([word_surface, x, y])
                if word_height > line_height:
                    line_height = word_height
                x += word_width + space
            text_map.append([current_line, x - space])
            x = 0
            y += line_height
            current_line = []
            all_lines_max_height += line_height

        if self.text_centered_y is True and all_lines_max_height < surface_max_height:
            shift_y = (surface_max_height - all_lines_max_height) / 2
        else:
            shift_y = 0

        for text_map_line in text_map:
            current_line, line_max_width = text_map_line
            if self.text_centered_x is True and line_max_width < surface_max_width:
                shift_x = (surface_max_width - line_max_width) / 2
            else:
                shift_x = 0

            for word_map in current_line:
                word_surface, x, y = word_map
                surface.blit(word_surface, (x + shift_x, y + shift_y))
