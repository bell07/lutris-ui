import pygame

from uiwidgets import UiWidget

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

    def compose_to_parent(self, surface: pygame.Surface) -> bool:
        # Do not use the "surface_for_childs".
        viewport_surface = self.parent_widget.get_surface(with_borders=False)
        if self.min_value >= self.max_value:
            return False

        if self.is_horizontal is True:
            max_value = viewport_surface.get_width() - SCROLLBAR_BORDER * 2
            max_height = viewport_surface.get_height()
            min_value = self.min_value * max_value / self.max_value
            cur_value = self.current_value * max_value / self.max_value
            pygame.draw.rect(viewport_surface, pygame.Color("Red"), (
                cur_value + SCROLLBAR_BORDER, max_height - SCROLLBAR_WIDTH - SCROLLBAR_BORDER, min_value,
                SCROLLBAR_WIDTH - 2 * SCROLLBAR_BORDER), border_radius=int(SCROLLBAR_WIDTH / 2))
        else:
            max_value = viewport_surface.get_height() - SCROLLBAR_BORDER * 2
            max_width = viewport_surface.get_width()
            min_value = self.min_value * max_value / self.max_value
            cur_value = self.current_value * max_value / self.max_value
            pygame.draw.rect(viewport_surface, pygame.Color("Red"), (
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
        self.vertical_scrollbar_widget = UiWidgetsScrollbar(self, is_horizontal=False)
        self.horizontal_scrollbar_widget = UiWidgetsScrollbar(self, is_horizontal=True)

    def get_surface_for_childs(self) -> pygame.Surface:
        (w, h) = self.get_rect(with_borders=False).size
        if self.viewport_width is None or self.viewport_height is None:
            if self.viewport_width is None:
                self.viewport_width = w
            if self.viewport_height is None:
                self.viewport_height = h
        if self._viewport_surface is None or self._viewport_surface.get_width() != self.viewport_width or \
                self._viewport_surface.get_height() != self.viewport_height:
            self._viewport_surface = pygame.surface.Surface((self.viewport_width, self.viewport_height))
            self.set_changed()
        return self._viewport_surface

    def get_size_for_childs(self) -> (int, int):
        return self.viewport_width, self.viewport_height

    def set_viewport_size(self, w: int, h: int) -> None:
        if self.viewport_width != w or self.viewport_height != h:
            self.viewport_width = w
            self.viewport_height = h
            self.set_changed()

    def adjust_shift(self):
        # Adjust shift
        shift_changed = False
        widget_rect = self.get_rect(with_borders=False)
        if self.viewport_width < self.shift_x + widget_rect.w:
            self.shift_x = self.viewport_width - widget_rect.w

        if self.viewport_height < self.shift_y + widget_rect.h:
            self.shift_y = self.viewport_height - widget_rect.h

        if self.shift_x < 0:
            self.shift_x = 0

        if self.shift_y < 0:
            self.shift_y = 0

        if self.shift_x != self._old_shift_x or self.shift_y != self._old_shift_y:
            shift_changed = True
            self._old_shift_x = self.shift_x
            self._old_shift_y = self.shift_y

        # Adjust scrollbars
        if self.vertical_scrollbar_widget is not None and (shift_changed is True or self.is_changed() is True):
            self.vertical_scrollbar_widget.min_value = widget_rect.h
            self.vertical_scrollbar_widget.max_value = self.viewport_height
            self.vertical_scrollbar_widget.current_value = self.shift_y
            self.vertical_scrollbar_widget.set_changed()

        if self.horizontal_scrollbar_widget is not None and (shift_changed is True or self.is_changed() is True):
            self.horizontal_scrollbar_widget.min_value = widget_rect.w
            self.horizontal_scrollbar_widget.max_value = self.viewport_width
            self.horizontal_scrollbar_widget.current_value = self.shift_x
            self.horizontal_scrollbar_widget.set_changed()

        return shift_changed

    def draw(self, force: bool = False) -> bool:
        if self.is_visible is False:
            return False

        if force is True:
            self.set_changed()

        updated = self.adjust_shift()
        # Scrollbars needs to be drawn after blit to parent surface
        self.vertical_scrollbar_widget.set_visible(False)
        self.horizontal_scrollbar_widget.set_visible(False)
        if super().draw(force) is True:
            updated = True

        if updated:
            widget_rect = self.get_rect(with_borders=False)
            widget_surface = self._viewport_surface.subsurface(
                (self.shift_x, self.shift_y, widget_rect.width, widget_rect.height))
            parent_surface = self.get_parent_surface()
            parent_surface.blit(widget_surface, widget_rect.topleft)

            self.vertical_scrollbar_widget.set_visible()
            self.vertical_scrollbar_widget.draw()
            self.horizontal_scrollbar_widget.set_visible()
            self.horizontal_scrollbar_widget.draw()
            self.unset_changed()

    def get_widget_collide_point(self, widget: UiWidget, pos: (int, int)) -> (int, int):
        pos_x, pos_y = pos
        shift_pos = (pos_x + self.shift_x, pos_y + self.shift_y)
        widget_rect = widget.get_rect(with_borders=False)
        if widget_rect.collidepoint(shift_pos):
            return shift_pos[0] - widget_rect.x, shift_pos[1] - widget_rect.y

    def process_events(self, events: list, pos: (int, int) = None) -> None:
        vertical_scrollbar_pointed = pos is not None and pos[0] > self.get_rect().width - SCROLLBAR_WIDTH * 2
        horizontal_scrollbar_pointed = pos is not None and pos[1] > self.get_rect().height - SCROLLBAR_WIDTH * 2
        scrolled = False

        # vertical scrollbar is pointed
        for e in events:
            if e.type == pygame.MOUSEMOTION:
                if vertical_scrollbar_pointed is True:
                    self.vertical_scrollbar_widget.process_events(events, pos)
                    return
                if horizontal_scrollbar_pointed is True:
                    self.horizontal_scrollbar_widget.process_events(events, pos)
                    return
                if e.touch is True:
                    self.shift_x = self.shift_x + (e.rel[0] * 5)
                    self.shift_y = self.shift_y - (e.rel[1] * 5)
                    self.set_changed()
                    scrolled = True
        if scrolled is False:
            super().process_events(events, pos)
