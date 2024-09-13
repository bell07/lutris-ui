import pygame

SCROLLBAR_WIDTH = 20  # Todo: Settings
SCROLLBAR_BORDER = 2


class UiWidget:
    def __init__(self, parent, def_x, def_y, def_w, def_h):
        self.parent_widget = None
        self.def_x = def_x
        self.def_y = def_y
        self.def_w = def_w
        self.def_h = def_h

        self._is_changed = True
        self.is_visible = True
        self.is_interactive = False
        self.is_focus = False

        self.widgets = []

        self._detached_surface = None
        self.set_parent_surface(parent)

    def set_parent_surface(self, parent):
        if hasattr(parent, "widgets"):  # Check if UiWidget compatible object
            self.parent_widget = parent
            parent.add_child(self)
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

    def compose_to_parent(self, surface):
        pass

    def is_changed(self):
        return self._is_changed is True

    def is_parent_changed(self):
        return (self.parent_widget and self.parent_widget.is_changed() is True) or False

    def set_changed(self, changed=True):
        self._is_changed = changed  # if self.parent_widget is not None:  #    self.parent_widget.set_changed()

    def draw(self, force=False):
        if self.is_visible is False:
            return

        if force is True or self.is_changed() is True or self.is_parent_changed() is True:
            self.compose_to_parent(self.get_parent_surface())
            self.set_changed()
        if force is True or self.is_changed() is True:
            self.compose(self.get_surface())

        for widget in self.widgets:
            widget.draw(force)
        self.set_changed(False)

    def add_child(self, widget) -> None:
        widget.parent_widget = self
        self.widgets.append(widget)

    def remove_child(self, widget) -> None:
        self.widgets.remove(widget)

    def process_events(self, events):
        for widget in self.widgets:
            # TODO: Check Focus
            widget.process_events(events)


class UiWidgetStatic(UiWidget):
    def __init__(self, parent, x, y, w, h):
        super().__init__(parent, x, y, w, h)
        self._widget_surface = None

    def init_widget_surface(self):
        parent_surface = self.get_parent_surface()
        self._widget_surface = pygame.Surface.copy(
            parent_surface.subsurface((self.get_widget_dimensions(parent_surface))))
        self.compose(self._widget_surface)
        return self._widget_surface

    def get_surface(self):
        if self._widget_surface is None:
            return self.init_widget_surface()
        return self._widget_surface

    def is_changed(self):
        # Parent changes not relevant
        return self._is_changed is True

    def draw(self, force=False):
        if self.is_visible is False:
            return
        if force is True or self._widget_surface is None:  # Force composing
            self.init_widget_surface()
            self.set_changed()

        # Rebuild, if changed or forced
        if force is True or self.is_parent_changed():
            parent_surface = self.get_parent_surface()
            widget_surface = self.get_surface()
            parent_surface.blit(widget_surface, self.get_widget_dimensions(parent_surface))
            self.compose_to_parent(parent_surface)
            self.set_changed()

        for widget in self.widgets:
            widget.draw(force)
        self.set_changed(False)


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

    def get_parent_surface(self):
        return self.parent_widget.get_visible_surface()

    def compose_to_parent(self, surface):
        if self.min_value >= self.max_value:
            return

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


class UiWidgetsViewport(UiWidgetStatic):
    def __init__(self, parent, x, y, w, h):
        super().__init__(parent, x, y, w, h)
        self.shift_x = 0
        self.shift_y = 0
        self._old_shift_x = None
        self._old_shift_y = None
        self.viewport_width = None
        self.viewport_height = None
        self.vertical_scrollbar_widget = None

    def set_viewport_size(self, w, h):
        self.viewport_width = w
        self.viewport_height = h

    def init_widget_surface(self):
        if self.viewport_width is None or self.viewport_height is None:
            _, _, w, h = self.get_widget_dimensions(self.get_parent_surface())
            if self.viewport_width is None:
                self.viewport_width = w
            if self.viewport_height is None:
                self.viewport_height = h
        self._widget_surface = pygame.surface.Surface((self.viewport_width, self.viewport_height))
        self.compose(self._widget_surface)
        return self._widget_surface

    def set_vertical_scrollbar(self, scrollbar_widget=None):
        if scrollbar_widget is None:
            # Create own widget
            self.vertical_scrollbar_widget = UiWidgetsScrollbar(self, False)
        else:
            self.vertical_scrollbar_widget = scrollbar_widget

    def get_visible_surface(self):
        viewport_surface = self.get_surface()
        parent_surface = self.get_parent_surface()
        x, y, w, h = self.get_widget_dimensions(parent_surface)
        return viewport_surface.subsurface((self.shift_x, self.shift_y, w, h))

    def draw(self, force=False):
        if self.is_visible is False:
            return

        # Adjust shift
        parent_surface = self.get_parent_surface()
        x, y, w, h = self.get_widget_dimensions(parent_surface)
        if self.viewport_width < self.shift_x + w:
            self.shift_x = self.viewport_width - w

        if self.viewport_height < self.shift_y + h:
            self.shift_y = self.viewport_height - h

        if self.shift_x != self._old_shift_x or self.shift_y != self._old_shift_y:
            self.set_changed()
            self._old_shift_x = self.shift_x
            self._old_shift_y = self.shift_y

        if force is True or self.is_changed() is True:
            self.init_widget_surface()

        # Adjust scrollbar
        visible_surface = self.get_visible_surface()
        if self.vertical_scrollbar_widget is not None:
            self.vertical_scrollbar_widget.min_value = h
            self.vertical_scrollbar_widget.max_value = self.viewport_height
            self.vertical_scrollbar_widget.current_value = self.shift_y

        # Draw viewport content
        super().draw(force)
        parent_surface.blit(visible_surface, (x, y))
        self.set_changed(False)
