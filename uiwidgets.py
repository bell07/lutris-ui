import pygame


class UiWidget:
    def __init__(self, surface, def_x, def_y, def_w, def_h):
        self.parent_surface = surface
        self.parent_widget = None
        self.is_changed = True
        self.widget_surface = None
        self.def_x = def_x
        self.def_y = def_y
        self.def_w = def_w
        self.def_h = def_h
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.adjust_dimensions()

    def adjust_dimensions(self):
        surface_w = self.parent_surface.get_width()
        surface_h = self.parent_surface.get_height()
        # Adjust x,y coordinates for top-left edge
        if self.def_x < 0:
            self.x = surface_w - self.def_x
            if self.x < 0:
                self.x = 0
        elif self.def_x > surface_w:
            self.x = surface_w
        else:
            self.x = self.def_x

        if self.def_y < 0:
            self.y = surface_h - self.def_y
            if self.y < 0:
                self.y = 0
        elif self.def_y > surface_h:
            self.y = surface_h
        else:
            self.y = self.def_y

        # Adjust width and height based on remaining space
        surface_w = surface_w - self.x
        surface_h = surface_h - self.y

        if self.def_w <= 0:
            self.w = surface_w + self.def_w
            if self.w < 0:
                self.w = 0
        elif self.def_w > surface_w:
            self.w = surface_w
        else:
            self.w = self.def_w

        if self.def_h <= 0:
            self.h = surface_h + self.def_h
            if self.h < 0:
                self.h = 0
        else:
            self.h = self.def_h
            if self.h > surface_h:
                self.h = surface_h

        self.widget_surface = self.parent_surface.subsurface((self.x, self.y, self.w, self.h))

    def compose(self):
        pass

    def draw(self, force=False):
        if self.is_changed is True or force is True:
            self.compose()
            self.is_changed = False

    def set_changed(self):
        self.is_changed = True
        if self.parent_widget is not None:
            self.parent_widget.set_changed()


class UiWidgetInteractive(UiWidget):
    def __init__(self, surface, x, y, w, h):
        super().__init__(surface, x, y, w, h)

    def process_events(self, events):
        pass


class UiWidgetsViewport(UiWidgetInteractive):
    def __init__(self, surface, x, y, w, h):
        self.shift_x = 0
        self.shift_y = 0
        self.viewport_surface = None
        super().__init__(surface, x, y, w, h)

    def set_viewport_size(self, w, h):
        self.viewport_surface = pygame.Surface((w, h))

    def compose(self):
        super().compose()
        visible_area = self.viewport_surface.subsurface((self.shift_x, self.shift_y, self.w, self.h))
        self.widget_surface.blit(visible_area, (0, 0))


class UiWidgetsContainer(UiWidgetInteractive):
    def __init__(self, surface, x, y, w, h):
        self.widgets = []
        super().__init__(surface, x, y, w, h)

    def add_widget(self, widget: UiWidget) -> None:
        widget.parent_widget = self
        self.widgets.append(widget)

    def compose(self):
        self.set_background()
        for widget in self.widgets:
            widget.compose()

    # abstract
    def set_background(self):
        pass

    def process_events(self, events):
        for widget in self.widgets:
            # TODO: Check Focus
            widget.process_events(events)

    def adjust_dimensions(self):
        super().adjust_dimensions()
        if self.widgets is not None:
            for widget in self.widgets:
                widget.parent_surface = self.widget_surface
                widget.adjust_dimensions()
