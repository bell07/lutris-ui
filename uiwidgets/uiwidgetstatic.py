from pygame import Surface, transform

from uiwidgets import UiWidget


class UiWidgetStatic(UiWidget):
    def __init__(self, parent: UiWidget, **kwargs):
        super().__init__(parent, **kwargs)
        self._widget_surface = None

    def get_surface(self) -> Surface:
        (w, h) = self.get_rect().size
        if self._widget_surface is None:
            self._widget_surface = Surface((w, h))
            self.set_changed()
        elif self._widget_surface.get_width() != w or \
                self._widget_surface.get_height() != h:
            self._widget_surface = transform.scale(self._widget_surface, (w, h))
            self.set_changed()
        return self._widget_surface

    def draw(self, force: bool = False, draw_to_parent: bool = True) -> bool:
        if self.is_visible is False:
            return False

        if force is True:
            self.set_changed()

        surface = self.get_surface()
        rect = self.get_rect()
        parent_surface = self.get_parent_surface()

        if draw_to_parent is True and (self.is_changed() is True or self.is_parent_changed()):
            if self.compose_to_parent(parent_surface, rect) is not False:
                self.parent_widget.set_child_changed()
            if self.compose_borders(parent_surface) is not False:
                self.parent_widget.set_child_changed()

        if self.is_changed() is True:
            if self.bg_color is not None:
                surface.fill(self.bg_color)
            self.compose(surface)

        if self.widgets is not None and (self._child_changed is True or self.is_changed() is True):
            for widget in self.widgets:
                widget.draw(force)

        updated = False
        if self._child_changed is True or self.is_parent_changed() is True or self.is_changed() is True:
            if draw_to_parent is True:
                parent_surface.blit(surface, rect)
            updated = True

        if draw_to_parent is True:
            self.unset_changed()
        return updated
