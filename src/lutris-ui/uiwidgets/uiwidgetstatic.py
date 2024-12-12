from pygame import Surface, transform, Rect

from uiwidgets import UiWidget


class UiWidgetStatic(UiWidget):
    def __init__(self, parent: UiWidget, alpha: int = None, surface_flags: int = 0, **kwargs):
        super().__init__(parent, **kwargs)
        self._widget_surface = None
        self._widget_surface_with_borders = None
        self.alpha = alpha
        self.surface_flags = surface_flags

    def get_surface(self, with_borders: bool = False) -> Surface:
        w, h = self.get_rect(with_borders=True).size
        if self._widget_surface_with_borders is None:
            self._widget_surface = None
            self._widget_surface_with_borders = Surface((w, h), flags=self.surface_flags)
            if self.alpha is not None:
                self._widget_surface_with_borders.set_alpha(self.alpha)
            self.set_changed()
        elif self._widget_surface_with_borders.get_width() != w or self._widget_surface_with_borders.get_height() != h:
            self._widget_surface = None
            self._widget_surface_with_borders = transform.scale(self._widget_surface_with_borders, (w, h))
            self.set_changed()
        if with_borders is True:
            return self._widget_surface_with_borders
        elif self._widget_surface is None:
            w, h = self.get_rect(with_borders=False).size
            self._widget_surface = self._widget_surface_with_borders.subsurface(
                Rect(self._dyn_rect.border_left, self._dyn_rect.border_top, w, h))
            if self.alpha is not None:
                self._widget_surface.set_alpha(self.alpha)
            self.set_changed()
        return self._widget_surface

    def set_border(self, **kwargs) -> None:
        super().set_border(**kwargs)
        self._widget_surface = None

    def set_alpha(self, alpha: int) -> None:
        self.alpha = alpha
        self.get_surface(with_borders=True).set_alpha(alpha)

    def draw(self) -> None:
        self.updated = False
        if self.is_visible is False:
            return

        compose_surface = self.get_surface(with_borders=False)  # Contain the check for surface changes
        if self.is_changed() is True:
            if self.bg_color is not None:
                self.get_surface(with_borders=True).fill(self.bg_color)
            self.compose(compose_surface)
            self.compose_borders()

        if self.widgets is not None and (self._child_changed is True or self.is_changed() is True):
            for widget in self.widgets:
                widget.draw()
                if widget.updated is True:
                    self.updated = True

        parent_surface = self.get_parent_surface()
        if self._child_changed is True or self.is_parent_changed() is True or self.is_changed() is True:
            parent_surface.blit(self.get_surface(with_borders=True), self.get_rect(with_borders=True))
            self.updated = True

        if self.updated is True:
            self.unset_changed()
