import pygame

from uiwidgets import UiWidget, UiWidgetStatic

SCROLLBAR_WIDTH = 20  # Todo: Settings
SCROLLBAR_BORDER = 2


class UiWidgetsScrollbar(UiWidget):
    def __init__(self, parent: UiWidget, is_horizontal: bool, **kwargs):
        super().__init__(parent, **kwargs)
        self.is_horizontal = is_horizontal
        if is_horizontal:
            self._dyn_rect.set_pos(pos_x=0, pos_y=-SCROLLBAR_WIDTH)
            self._dyn_rect.set_size(size_h=SCROLLBAR_WIDTH)
        else:
            self._dyn_rect.set_pos(pos_x=-SCROLLBAR_WIDTH, pos_y=0)
            self._dyn_rect.set_size(size_w=SCROLLBAR_WIDTH)
        self.auto_hide = True
        self.current_value = 0
        self.min_value = 0
        self.max_value = 0

    def get_parent_surface(self) -> pygame.Surface:
        if self._parent_surface is None or self.is_parent_changed():
            self._parent_surface = self.parent_widget.get_visible_surface()
        return self._parent_surface

    def get_parent_size(self) -> (int, int):
        return self.get_parent_surface().get_size()

    def compose_to_parent(self, surface: pygame.Surface) -> bool:
        if self.min_value >= self.max_value:
            return False

        if self.is_horizontal is True:
            max_value = surface.get_width() - SCROLLBAR_BORDER * 2
            max_height = surface.get_height()
            min_value = self.min_value * max_value / self.max_value
            cur_value = self.current_value * max_value / self.max_value
            pygame.draw.rect(surface, pygame.colordict.THECOLORS["red"], (
                cur_value + SCROLLBAR_BORDER, max_height - SCROLLBAR_WIDTH - SCROLLBAR_BORDER, min_value,
                SCROLLBAR_WIDTH - 2 * SCROLLBAR_BORDER), border_radius=int(SCROLLBAR_WIDTH / 2))
        else:
            max_value = surface.get_height() - SCROLLBAR_BORDER * 2
            max_width = surface.get_width()
            min_value = self.min_value * max_value / self.max_value
            cur_value = self.current_value * max_value / self.max_value
            pygame.draw.rect(surface, pygame.colordict.THECOLORS["red"], (
                max_width - SCROLLBAR_WIDTH - SCROLLBAR_BORDER, cur_value + SCROLLBAR_BORDER,
                SCROLLBAR_WIDTH - 2 * SCROLLBAR_BORDER, min_value), border_radius=int(SCROLLBAR_WIDTH / 2))

    def process_events(self, events: list, pos: (int, int) = None) -> None:
        for e in events:
            match e.type:
                case pygame.MOUSEMOTION:
                    if pygame.BUTTON_LEFT in e.buttons:
                        if self.is_horizontal is True:
                            self.parent_widget.shift_x = self.parent_widget.shift_x + (
                                    e.rel[0] / self.min_value * self.max_value)
                        else:
                            self.parent_widget.shift_y = self.parent_widget.shift_y + (
                                    e.rel[1] / self.min_value * self.max_value)
                        self.set_changed()


class UiWidgetViewport(UiWidgetStatic):
    def __init__(self, parent: UiWidget, **kwargs):
        super().__init__(parent, **kwargs)
        self.shift_x = 0
        self.shift_y = 0
        self._old_shift_x = None
        self._old_shift_y = None
        self.viewport_width = None
        self.viewport_height = None
        self.vertical_scrollbar_widget = UiWidgetsScrollbar(self, False)

    def set_viewport_size(self, w: int, h: int) -> None:
        if self.viewport_width != w or self.viewport_height != h:
            self.viewport_width = w
            self.viewport_height = h
            self.set_changed()

    def get_surface(self) -> pygame.Surface:
        (w, h) = self.get_rect().size
        if self.viewport_width is None or self.viewport_height is None:
            if self.viewport_width is None:
                self.viewport_width = w
            if self.viewport_height is None:
                self.viewport_height = h
        if self._widget_surface is None or self._widget_surface.get_width() != self.viewport_width or \
                self._widget_surface.get_height() != self.viewport_height:
            self._widget_surface = pygame.surface.Surface((self.viewport_width, self.viewport_height))
            self.set_changed()
        return self._widget_surface

    def get_size(self) -> (int, int):
        return self.get_surface().get_size()

    def get_visible_surface(self) -> pygame.Surface:
        viewport_surface = self.get_surface()
        (w, h) = self.get_rect().size
        return viewport_surface.subsurface((self.shift_x, self.shift_y, w, h))

    def draw(self, force: bool = False, draw_to_parent: bool = True) -> bool:
        if self.is_visible is False:
            return False

        if force is True:
            self.set_changed()

        # Adjust shift
        widget_rect = self.get_rect()
        if self.viewport_width < self.shift_x + widget_rect.w:
            self.shift_x = self.viewport_width - widget_rect.w

        if self.viewport_height < self.shift_y + widget_rect.h:
            self.shift_y = self.viewport_height - widget_rect.h

        if self.shift_x < 0:
            self.shift_x = 0

        if self.shift_y < 0:
            self.shift_y = 0

        if self.shift_x != self._old_shift_x or self.shift_y != self._old_shift_y:
            self.set_changed()
            self._old_shift_x = self.shift_x
            self._old_shift_y = self.shift_y

        # Adjust scrollbar
        if self.vertical_scrollbar_widget is not None:
            self.vertical_scrollbar_widget.min_value = widget_rect.h
            self.vertical_scrollbar_widget.max_value = self.viewport_height
            self.vertical_scrollbar_widget.current_value = self.shift_y
            self.vertical_scrollbar_widget.set_visible(False)

        # Draw viewport content
        updated = super().draw(force, draw_to_parent=False)
        if updated is True or self.is_parent_changed() is True:
            # Adjust scrollbar
            if self.vertical_scrollbar_widget is not None:
                self.vertical_scrollbar_widget.set_visible(True)
                self.vertical_scrollbar_widget.set_changed()
                self.vertical_scrollbar_widget.draw(force)

            if draw_to_parent is True:
                visible_surface = self.get_visible_surface()
                parent_surface = self.get_parent_surface()
                parent_surface.blit(visible_surface, widget_rect.topleft)
        if draw_to_parent is True:
            self.unset_changed()
        return updated

    def get_widget_collide_point(self, widget: UiWidget, pos: (int, int)) -> (int, int):
        pos_x, pos_y = pos
        shift_pos = (pos_x + self.shift_x, pos_y + self.shift_y)
        widget_rect = widget.get_rect()
        if widget_rect.collidepoint(shift_pos):
            return shift_pos[0] - widget_rect.x, shift_pos[1] - widget_rect.y

    def process_events(self, events: list, pos: (int, int) = None) -> None:
        vertical_scrollbar_pointed = pos is not None and pos[0] > self.get_rect().width - SCROLLBAR_WIDTH * 2
        scrolled = False

        # vertical scrollbar is pointed
        for e in events:
            if e.type == pygame.MOUSEMOTION:
                if vertical_scrollbar_pointed is True:
                    self.vertical_scrollbar_widget.process_events(events, pos)
                    return
                if e.touch is True:
                    self.shift_x = self.shift_x + (e.rel[0] * 5)
                    self.shift_y = self.shift_y - (e.rel[1] * 5)
                    self.set_changed()
                    scrolled = True
        if scrolled is False:
            super().process_events(events, pos)
