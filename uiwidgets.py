import pygame

SCROLLBAR_WIDTH = 20  # Todo: Settings
SCROLLBAR_BORDER = 2


class UiWidget:
    def __init__(self, parent, def_x, def_y, def_w, def_h):
        self.parent_widget = None
        self._widget_dimensions = None
        self._parent_surface = None
        self.def_x = def_x
        self.def_y = def_y
        self.def_w = def_w
        self.def_h = def_h

        self._is_changed = True
        self._child_changed = True

        self.is_visible = True
        self.is_interactive = True
        self.is_focus = False

        self.widgets = []
        self.selected_widget = None

        self._detached_surface = None
        self.set_parent_surface(parent)

    def set_parent_surface(self, parent):
        if isinstance(parent, UiWidget):  # Check if UiWidget compatible object
            self.parent_widget = parent
            parent.add_child(self)
            self._detached_surface = None
        else:
            self._detached_surface = parent
        self._parent_surface = None
        self._widget_dimensions = None

    def get_parent_surface(self):
        if self._parent_surface is not None and self.is_parent_changed() is False:
            return self._parent_surface

        if self._detached_surface is None:
            self._parent_surface = self.parent_widget.get_surface()
        else:
            self._parent_surface = self._detached_surface

        return self._parent_surface

    def get_surface(self):
        parent_surface = self.get_parent_surface()
        return parent_surface.subsurface((self.get_widget_dimensions()))

    def get_widget_dimensions(self, surface=None):
        if surface is None and self._widget_dimensions is not None:
            return self._widget_dimensions

        chk_surface = surface or self.get_parent_surface()

        surface_w = chk_surface.get_width()
        surface_h = chk_surface.get_height()
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

        dimensions = pygame.Rect(ret_x, ret_y, ret_w, ret_h)
        if surface is None:
            self._widget_dimensions = dimensions
        return dimensions

    def compose(self, surface):
        return False

    def compose_to_parent(self, surface):
        return False

    def is_changed(self):
        return self._is_changed is True

    def is_parent_changed(self):
        return (self.parent_widget and self.parent_widget.is_changed() is True) or False

    def set_changed(self):
        self._is_changed = True
        self._widget_dimensions = None
        self._parent_surface = None
        self.parent_widget and self.parent_widget.set_child_changed()

    def set_child_changed(self):
        if self._child_changed is False:
            self._child_changed = True
            if self.parent_widget is not None:
                self.parent_widget.set_child_changed()

    def unset_changed(self):
        self._is_changed = False
        self._child_changed = False

    def set_focus(self, focus=True):
        if self.is_focus != focus:
            if focus is True and self.parent_widget is not None:
                for widget in self.parent_widget.widgets:
                    if widget != self:
                        widget.set_focus(False)
            self.is_focus = focus
            self.set_changed()
            if self.parent_widget is not None:
                self.parent_widget.set_focus(focus)

    def draw(self, force=False):
        if self.is_visible is False:
            return

        if force is True:
            self.set_changed()

        updated = False
        if self.is_changed() is True or self.is_parent_changed():
            if self.compose_to_parent(self.get_parent_surface()) is not False:
                self.set_changed()
            if self.compose(self.get_surface()) is not False:
                self.set_changed()

        if self._child_changed is True or self.is_changed() is True:
            for widget in self.widgets:
                widget.draw(force)
            updated = True

        self.unset_changed()
        return updated

    def add_child(self, widget) -> None:
        widget.parent_widget = self
        self.widgets.append(widget)

    def remove_child(self, widget) -> None:
        self.widgets.remove(widget)

    def get_child_by_pos(self, pos):
        if self.get_widget_dimensions().collidepoint(pos) is False:
            return
        for widget in self.widgets:
            if widget.is_interactive is True:
                if widget.get_widget_dimensions().collidepoint(pos) is True:
                    return widget

    def process_events(self, events):
        for e in events:
            match e.type:
                case pygame.MOUSEBUTTONUP:
                    if e.button <= 3:  # 4 and 5 are wheel
                        selected_widget = self.get_child_by_pos(e.pos)
                        if selected_widget is not None and selected_widget.is_interactive is True:
                            self.selected_widget = selected_widget
                            self.selected_widget.set_focus()

        for widget in self.widgets:
            if widget.is_interactive is False:
                continue
            widget_events = []
            for e in events:
                if hasattr(e, "pos"):
                    widget_rect = widget.get_widget_dimensions()
                    if widget_rect.collidepoint(e.pos):
                        event_data = e.dict.copy()
                        event_data["pos"] = (e.pos[0] - widget_rect.x, e.pos[1] - widget_rect.y)
                        widget_event = pygame.event.Event(e.type, event_data)
                        widget_events.append(widget_event)  # Position inside the widget. Pass event
                elif widget.is_focus is True:
                    widget_events.append(e)  # Position-less events to widget with focus only

            widget.process_events(widget_events)


class UiWidgetStatic(UiWidget):
    def __init__(self, parent, x, y, w, h):
        super().__init__(parent, x, y, w, h)
        self._widget_surface = None

    def get_surface(self):
        if self._widget_surface is None:
            self._widget_surface = pygame.Surface(self.get_widget_dimensions().size)
        return self._widget_surface

    def draw(self, force=False, draw_to_parent=True):
        if self.is_visible is False:
            return

        if force is True:
            self.set_changed()

        updated = False
        if draw_to_parent is True and (self.is_changed() is True or self.is_parent_changed()):
            parent_surface = self.get_parent_surface()
            if self.compose_to_parent(parent_surface) is not False:
                parent_surface.set_child_changed()

        if self._widget_surface is None or self.is_changed() is True:
            self._widget_surface = None  # Force rebuild
            if self.compose(self.get_surface()) is not False:
                self.set_changed()

        if self._child_changed is True or self.is_changed() is True:
            for widget in self.widgets:
                widget.draw(force)

        if self._child_changed is True or self.is_parent_changed() is True or self.is_changed() is True:
            if draw_to_parent is True:
                parent_surface = self.get_parent_surface()
                widget_surface = self.get_surface()
                parent_surface.blit(widget_surface, self.get_widget_dimensions())
            updated = True

        self.unset_changed()
        return updated


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
        if self._parent_surface is None:
            self._parent_surface = self.parent_widget.get_visible_surface()
        return self._parent_surface

    def compose_to_parent(self, surface):
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

    def process_events(self, events):
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


class UiWidgetsViewport(UiWidgetStatic):
    def __init__(self, parent, x, y, w, h):
        super().__init__(parent, x, y, w, h)
        self.shift_x = 0
        self.shift_y = 0
        self._old_shift_x = None
        self._old_shift_y = None
        self.viewport_width = None
        self.viewport_height = None
        self.vertical_scrollbar_widget = UiWidgetsScrollbar(self, False)

    def set_viewport_size(self, w, h):
        self.viewport_width = w
        self.viewport_height = h
        self.set_changed()

    def get_surface(self):
        if self._widget_surface is None:
            self.init_widget_surface()
        return self._widget_surface

    def init_widget_surface(self):
        if self.viewport_width is None or self.viewport_height is None:
            widget_rect = self.get_widget_dimensions()
            if self.viewport_width is None:
                self.viewport_width = widget_rect.w
            if self.viewport_height is None:
                self.viewport_height = widget_rect.h
        self._widget_surface = pygame.surface.Surface((self.viewport_width, self.viewport_height))
        return self._widget_surface

    def get_visible_surface(self):
        viewport_surface = self.get_surface()
        widget_rect = self.get_widget_dimensions()
        return viewport_surface.subsurface((self.shift_x, self.shift_y, widget_rect.w, widget_rect.h))

    def draw(self, force=False, draw_to_parent=True):
        if self.is_visible is False:
            return

        if force is True:
            self.set_changed()

        # Adjust shift
        widget_rect = self.get_widget_dimensions()
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
            self.vertical_scrollbar_widget.is_visible = False  # Draw on top later

        # Draw viewport content
        updated = super().draw(force, draw_to_parent=False)
        if updated is True or self.is_parent_changed() is True:
            # Adjust scrollbar
            if self.vertical_scrollbar_widget is not None:
                self.vertical_scrollbar_widget.is_visible = True
                self.vertical_scrollbar_widget.set_changed()
                self.vertical_scrollbar_widget.draw(force)

            if draw_to_parent is True:
                visible_surface = self.get_visible_surface()
                parent_surface = self.get_parent_surface()
                parent_surface.blit(visible_surface, widget_rect.topleft)
            self.unset_changed()
        return updated

    def get_child_by_pos(self, pos):
        # Check if viewport is pointed
        if self.get_widget_dimensions().collidepoint(pos):
            pos_x, pos_y = pos
            shift_pos = (pos_x + self.shift_x, pos_y + self.shift_y)
            for widget in self.widgets:
                if widget.is_interactive is False:
                    continue
                if widget.get_widget_dimensions().collidepoint(shift_pos) is True:
                    return widget
