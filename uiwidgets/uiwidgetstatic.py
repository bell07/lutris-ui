from pygame import Surface

from uiwidgets import UiWidget


class UiWidgetStatic(UiWidget):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._widget_surface = None

    def get_surface(self):
        (w, h) = self.get_rect().size
        if self._widget_surface is None or self._widget_surface.get_width() != w or \
                self._widget_surface.get_height() != h:
            self._widget_surface = Surface((w, h))
            self.set_changed()
        return self._widget_surface

    def draw(self, force=False, draw_to_parent=True):
        if self.is_visible is False:
            return

        if force is True:
            self.set_changed()

        surface = self.get_surface()
        parent_surface = self.get_parent_surface()

        if draw_to_parent is True and (self.is_changed() is True or self.is_parent_changed()):
            if self.compose_to_parent(parent_surface) is not False:
                parent_surface.set_child_changed()

        if self.is_changed() is True:
            if self.compose(surface) is not False:
                # self.set_changed()
                pass

        if self._child_changed is True or self.is_changed() is True:
            for widget in self.widgets:
                widget.draw(force)

        updated = False
        if self._child_changed is True or self.is_parent_changed() is True or self.is_changed() is True:
            if draw_to_parent is True:
                parent_surface.blit(surface, self.get_rect())
            updated = True

        if draw_to_parent is True:
            self.unset_changed()
        return updated
