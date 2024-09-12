import pygame

SCROLLBAR_WIDTH = 20  # Todo: Settings
SCROLLBAR_BORDER = 2


class UiWidget:
    def __init__(self, parent, def_x, def_y, def_w, def_h):
        self.parent_widget = None
        self._detached_surface = None
        self.set_parent_surface(parent)
        self.is_changed = True
        self.is_visible = True
        self.def_x = def_x
        self.def_y = def_y
        self.def_w = def_w
        self.def_h = def_h

    def set_parent_surface(self, parent):
        if hasattr(parent, "widgets"):  # Check if UiWidget compatible object
            self.parent_widget = parent
            self._detached_surface = None
        else:
            self._detached_surface = parent

    def get_parent_surface(self):
        if self._detached_surface is None:
            return self.parent_widget.get_surface()
        else:
            return self._detached_surface

    def get_surface(self):
        parent_surface = self.get_parent_surface()
        return parent_surface.subsurface((self.get_widget_dimensions(parent_surface)))

    def get_widget_dimensions(self, parent_surface):
        surface_w = parent_surface.get_width()
        surface_h = parent_surface.get_height()
        # Adjust x,y coordinates for top-left edge
        if self.def_x < 0:
            ret_x = surface_w + self.def_x
            if ret_x < 0:
                ret_x = 0
        elif self.def_x > surface_w:
            ret_x = surface_w
        else:
            ret_x = self.def_x

        if self.def_y < 0:
            ret_y = surface_h + self.def_y
            if ret_y < 0:
                ret_y = 0
        elif self.def_y > surface_h:
            ret_y = surface_h
        else:
            ret_y = self.def_y

        # Adjust width and height based on remaining space
        surface_w = surface_w - ret_x
        surface_h = surface_h - ret_y

        if self.def_w <= 0:
            ret_w = surface_w + self.def_w
            if ret_w < 0:
                ret_w = 0
        elif self.def_w > surface_w:
            ret_w = surface_w
        else:
            ret_w = self.def_w

        if self.def_h <= 0:
            ret_h = surface_h + self.def_h
            if ret_h < 0:
                ret_h = 0
        else:
            ret_h = self.def_h
            if ret_h > surface_h:
                ret_h = surface_h

        return ret_x, ret_y, ret_w, ret_h

    def compose(self, surface):
        pass

    def draw(self, force=False, parent_updated=False):
        if self.is_visible is False:
            return
        # Rebuild, if changed or forced, or parent updated
        if self.is_changed is True or parent_updated is True or force is True:
            # Compose directly in sub-surface
            self.compose(self.get_surface())
            self.is_changed = False

    def set_changed(self):
        self.is_changed = True
        if self.parent_widget is not None:
            self.parent_widget.set_changed()

    def process_events(self, events):
        pass


class UiWidgetStatic(UiWidget):
    def __init__(self, parent, x, y, w, h):
        super().__init__(parent, x, y, w, h)
        self._widget_surface = None

    def init_widget_surface(self):
        parent_surface = self.get_parent_surface()
        self._widget_surface = pygame.Surface.copy(
            parent_surface.subsurface((self.get_widget_dimensions(parent_surface))))
        return self._widget_surface

    def get_surface(self):
        if self._widget_surface is None:
            self.compose(self.init_widget_surface())
        return self._widget_surface

    def draw(self, force=False, parent_updated=False):
        if force is True:  # Force composing
            self.compose(self.init_widget_surface())

        # Rebuild, if changed or forced
        if self.is_changed is True or parent_updated is True or force is True:
            parent_surface = self.get_parent_surface()
            widget_surface = self.get_surface()
            parent_surface.blit(widget_surface, self.get_widget_dimensions(parent_surface))
            self.is_changed = False


class UiWidgetsContainer(UiWidget):
    def __init__(self, parent, x, y, w, h):
        super().__init__(parent, x, y, w, h)
        self.widgets = []

    def add_widget(self, widget: UiWidget) -> None:
        widget.parent_widget = self
        self.widgets.append(widget)

    def remove_widget(self, widget: UiWidget) -> None:
        self.widgets.remove(widget)

    def draw(self, force=False, parent_updated=False):
        for widget in self.widgets:
            widget.draw(force, parent_updated)
        self.is_changed = False

    def process_events(self, events):
        for widget in self.widgets:
            # TODO: Check Focus
            widget.process_events(events)


class UiWidgetsScrollbar(UiWidget):
    def __init__(self, parent, is_horizontal, x=None, y=None, w=None, h=None):
        self.is_horizontal = is_horizontal
        if is_horizontal:
            x = x or 0
            y = y or -SCROLLBAR_WIDTH
            w = w or 0
            h = h or SCROLLBAR_WIDTH
        else:
            x = x or -SCROLLBAR_WIDTH
            y = y or 0
            w = w or SCROLLBAR_WIDTH
            h = h or 0

        super().__init__(parent, x, y, w, h)
        self.auto_hide = True
        self.current_value = 0
        self.min_value = 0
        self.max_value = 0

    def compose(self, surface):
        surface.fill((128, 128, 128))
        if self.is_horizontal is True:
            max_value = surface.get_width()
            min_value = self.min_value * max_value / self.max_value
            cur_value = self.current_value * max_value / self.max_value
            pygame.draw.rect(surface, pygame.colordict.THECOLORS["red"],
                             (cur_value, SCROLLBAR_BORDER, min_value, SCROLLBAR_WIDTH - 2 * SCROLLBAR_BORDER),
                             border_radius=int(SCROLLBAR_WIDTH / 2))
        else:
            max_value = surface.get_height()
            min_value = self.min_value * max_value / self.max_value
            cur_value = self.current_value * max_value / self.max_value
            pygame.draw.rect(surface, pygame.colordict.THECOLORS["red"],
                             (SCROLLBAR_BORDER, cur_value, SCROLLBAR_WIDTH - 2 * SCROLLBAR_BORDER, min_value),
                             border_radius=int(SCROLLBAR_WIDTH / 2))

    def draw(self, force=False, parent_updated=False):
        if self.auto_hide is True and self.current_value == 0 and self.min_value >= self.max_value:
            return  # Auto-Hidden
        super().draw(force, parent_updated)


class UiWidgetsViewport(UiWidgetsContainer, UiWidgetStatic):
    def __init__(self, parent, x, y, w, h):
        super().__init__(parent, x, y, w, h)
        self.shift_x = 0
        self.shift_y = 0
        self.viewport_width = None
        self.viewport_height = None
        self.vertical_scrollbar_widget = None

    def set_viewport_size(self, w, h):
        self.viewport_width = w
        self.viewport_height = h
        self.init_widget_surface()

    def init_widget_surface(self):
        if self.viewport_width is None or self.viewport_height is None:
            _, _, w, h = self.get_widget_dimensions(self.get_parent_surface())
            if self.viewport_width is None:
                self.viewport_width = w
            if self.viewport_height is None:
                self.viewport_height = h
        self._widget_surface = pygame.surface.Surface((self.viewport_width, self.viewport_height))
        self.set_changed()
        return self._widget_surface

    def set_vertical_scrollbar(self, scrollbar_widget=None):
        if scrollbar_widget is None:
            # Create own widget
            self.vertical_scrollbar_widget = UiWidgetsScrollbar(self, False)
        else:
            self.vertical_scrollbar_widget = scrollbar_widget

    def draw(self, force=False, parent_updated=False):
        # TODO: Check if draw is necessary
        self.compose(self.get_surface())  # Draw background
        super().draw(force, parent_updated=True)
        viewport_surface = self.get_surface()
        parent_surface = self.get_parent_surface()
        x, y, w, h = self.get_widget_dimensions(parent_surface)
        if self.viewport_width < self.shift_x + w:
            self.shift_x = self.viewport_width - w

        if self.viewport_height < self.shift_y + h:
            self.shift_y = self.viewport_height - h

        visible_area = viewport_surface.subsurface((self.shift_x, self.shift_y, w, h))
        if self.vertical_scrollbar_widget is not None:
            self.vertical_scrollbar_widget.min_value = h
            self.vertical_scrollbar_widget.max_value = viewport_surface.get_height()
            self.vertical_scrollbar_widget.current_value = self.shift_y
            self.vertical_scrollbar_widget.set_parent_surface(visible_area)
            self.vertical_scrollbar_widget.draw(force, parent_updated)

        parent_surface.blit(visible_area, (x, y))
