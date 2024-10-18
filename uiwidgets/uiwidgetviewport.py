import pygame

from uiwidgets import UiWidget


class UiWidgetsScrollbar(UiWidget):
    def __init__(self, parent: UiWidget, scrollbar_is_horizontal: bool, scrollbar_width: float = 20,
                 scrollbar_color: pygame.Color = "Red", **kwargs):
        super().__init__(parent, **kwargs)
        self.scrollbar_is_horizontal = scrollbar_is_horizontal
        self.scrollbar_width = scrollbar_width
        self.scrollbar_color = scrollbar_color
        if scrollbar_is_horizontal:
            self._dyn_rect.set_pos(pos_x=0, pos_y=-0.1)
            self._dyn_rect.set_size(size_h=self.scrollbar_width)
        else:
            self._dyn_rect.set_pos(pos_x=-0.1, pos_y=0)
            self._dyn_rect.set_size(size_w=self.scrollbar_width)
        self.current_value = 0
        self.bar_value = 0
        self.max_value = 0

    def adjust_scrollbar_by_viewport(self):
        viewport_widget = self.parent_widget.viewport_widget
        viewport_width, viewport_height = viewport_widget.get_size(with_borders=True)
        window_width, window_height = self.get_parent_size()

        if self.scrollbar_is_horizontal is True:
            if self.bar_value != window_width or self.max_value != viewport_width or \
                    self.current_value != viewport_widget.shift_x:
                self.bar_value = window_width
                self.max_value = viewport_width
                self.current_value = viewport_widget.shift_x
                self.set_changed()
        else:
            if self.bar_value != window_height or self.max_value != viewport_height or \
                    self.current_value != viewport_widget.shift_y:
                self.bar_value = window_height
                self.max_value = viewport_height
                self.current_value = viewport_widget.shift_y
                self.set_changed()

        if self.is_changed() is True:
            if self.bar_value >= self.max_value:
                self.set_visible(False)
            else:
                self.set_visible(True)

    def draw(self) -> None:
        if self.parent_widget.viewport_widget.updated:
            self.adjust_scrollbar_by_viewport()
        super().draw()

    def compose(self, surface: pygame.Surface) -> bool:
        scrollbar_width, scrollbar_height = self.get_size(with_borders=False)

        if self.scrollbar_is_horizontal is True:
            scrollbar_x = self.current_value * scrollbar_width / self.max_value
            scrollbar_w = self.bar_value * scrollbar_width / self.max_value
            pygame.draw.rect(surface, self.scrollbar_color,
                             (scrollbar_x, 0, scrollbar_w, self.scrollbar_width),
                             border_radius=int(self.scrollbar_width / 2))
        else:
            scrollbar_y = self.current_value * scrollbar_height / self.max_value
            scrollbar_h = self.bar_value * scrollbar_height / self.max_value
            pygame.draw.rect(surface, self.scrollbar_color,
                             (0, scrollbar_y, self.scrollbar_width, scrollbar_h),
                             border_radius=int(self.scrollbar_width / 2))
        return True

    def process_events(self, events: list, pos: (int, int) = None) -> None:
        for e in events:
            match e.type:
                case pygame.MOUSEMOTION:
                    if pygame.BUTTON_LEFT in e.buttons:
                        viewport_widget = self.parent_widget.viewport_widget
                        if self.scrollbar_is_horizontal is True:
                            viewport_widget.shift_x = viewport_widget.shift_x + (
                                    e.rel[0] / self.bar_value * self.max_value)
                        else:
                            viewport_widget.shift_y = viewport_widget.shift_y + (
                                    e.rel[1] / self.bar_value * self.max_value)
                        viewport_widget.set_changed()


class UiWidgetViewport(UiWidget):
    def __init__(self, parent: UiWidget, **kwargs):
        super().__init__(parent, **kwargs)
        self.shift_x = 0
        self.shift_y = 0
        self._old_shift_x = None
        self._old_shift_y = None
        self.viewport_width = None
        self.viewport_height = None
        self._viewport_surface = None

    def set_size(self, w: int, h: int) -> None:
        parent_width, parent_height = self.get_parent_size()
        width_with_border = w + self._dyn_rect.border_left + self._dyn_rect.border_right
        if width_with_border < parent_width:
            width_with_border = parent_width
        height_with_border = h + self._dyn_rect.border_top + self._dyn_rect.border_bottom
        if height_with_border < parent_height:
            height_with_border = parent_height

        if self.viewport_width != width_with_border or self.viewport_height != height_with_border:
            self.viewport_width = width_with_border
            self.viewport_height = height_with_border
            self.set_changed()

    def get_surface(self, with_borders: bool = False) -> pygame.Surface:
        size = self.get_size(with_borders)
        if with_borders is True:
            pos = (0, 0)
        else:
            pos = (self._dyn_rect.border_left, self._dyn_rect.border_top)
        return self._viewport_surface.subsurface(pygame.Rect(pos, size))

    def get_rect(self, with_borders: bool = False) -> pygame.Rect:
        parent_width, parent_height = self.get_parent_size()
        if self.viewport_width is None or self.viewport_height is None:
            if self.viewport_width is None:
                self.viewport_width = parent_width
            if self.viewport_height is None:
                self.viewport_height = parent_height
        if self._viewport_surface is None or self._viewport_surface.get_width() != self.viewport_width or \
                self._viewport_surface.get_height() != self.viewport_height:
            self._viewport_surface = pygame.surface.Surface((self.viewport_width, self.viewport_height))
            self.set_changed()
        self._dyn_rect.set_parent_size(self.viewport_width, self.viewport_height)
        return self._dyn_rect.get_rect(with_borders)

    def adjust_shift(self):
        # Adjust shift
        shift_changed = False
        parent_width, parent_height = self.get_parent_size()
        if self.viewport_width < self.shift_x + parent_width:
            self.shift_x = self.viewport_width - parent_width

        if self.viewport_height < self.shift_y + parent_height:
            self.shift_y = self.viewport_height - parent_height

        if self.shift_x < 0:
            self.shift_x = 0

        if self.shift_y < 0:
            self.shift_y = 0

        if self.shift_x != self._old_shift_x or self.shift_y != self._old_shift_y:
            shift_changed = True
            self._old_shift_x = self.shift_x
            self._old_shift_y = self.shift_y
        return shift_changed

    def draw(self) -> None:
        self.updated = False
        if self.is_visible is False:
            return

        if self.adjust_shift():
            self.set_changed()

        super().draw()
        if self.updated:
            parent_surface = self.get_parent_surface()
            parent_width, parent_height = self.get_parent_size()
            widget_surface = self._viewport_surface.subsurface(
                (self.shift_x, self.shift_y, parent_width, parent_height))
            parent_surface.blit(widget_surface, (0, 0))
            self.unset_changed()

    def get_widget_collide_point(self, widget: UiWidget, pos: (int, int)) -> (int, int):
        pos_x, pos_y = pos
        shift_pos = (pos_x + self.shift_x, pos_y + self.shift_y)
        widget_rect = widget.get_rect(with_borders=False)
        if widget_rect.collidepoint(shift_pos):
            return shift_pos[0] - widget_rect.x, shift_pos[1] - widget_rect.y

    def process_events(self, events: list, pos: (int, int) = None) -> None:
        scrolled = False

        # vertical scrollbar is pointed
        for e in events:
            if e.type == pygame.MOUSEMOTION and e.touch is True:
                self.shift_x = self.shift_x + (e.rel[0] * 5)
                self.shift_y = self.shift_y - (e.rel[1] * 5)
                self.set_changed()
                scrolled = True
        if scrolled is False:
            super().process_events(events, pos)


class UiWidgetViewportContainer(UiWidget):
    def __init__(self, parent: UiWidget, **kwargs):
        super().__init__(parent, **kwargs)
        self.viewport_widget = None
        self.vertical_scrollbar_widget = UiWidgetsScrollbar(self, scrollbar_is_horizontal=False)
        self.horizontal_scrollbar_widget = UiWidgetsScrollbar(self, scrollbar_is_horizontal=True)

    def set_viewport_widget(self, widget: UiWidgetViewport):
        self.viewport_widget = widget
        # Move viewport on top
        self.widgets.remove(widget)
        self.widgets.insert(0, widget)
