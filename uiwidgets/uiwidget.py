# import pygame
from __future__ import annotations

from pygame import Surface, Rect, Color, constants, draw

from uiwidgets import DynamicRect


class UiWidget:
    def __init__(self, parent: UiWidget = None, bg_color: Color = None, border_color: Color = None, **kwargs):
        self.parent_widget = None
        self._parent_surface = None
        self._dyn_rect = DynamicRect(**kwargs)
        self._is_changed = True
        self._child_changed = True

        self.is_visible = True
        self.is_interactive = True
        self.is_focus = False
        self.updated = False

        self.widgets = None
        self.focus_child = None
        self.bg_color = bg_color
        self.border_color = border_color

        parent and self.set_parent_surface(parent)

    def set_parent_surface(self, parent: UiWidget) -> None:
        self.parent_widget = parent
        parent.add_child(self)
        self._dyn_rect.set_parent_size_by_surface(parent.get_surface(with_borders=False))
        self._parent_surface = None

    def get_root_widget(self):  # -> No annotation because root type "unknown/custom"
        if self.parent_widget is not None:
            return self.parent_widget.get_root_widget()
        else:
            return self

    def get_parent_surface(self) -> Surface:
        if self._parent_surface is None or self.is_parent_changed() is True:
            self._parent_surface = self.parent_widget.get_surface(with_borders=False)
        return self._parent_surface

    def get_parent_size(self) -> (int, int):
        return self.parent_widget.get_size(with_borders=False)

    def get_rect(self, with_borders: bool = False) -> Rect:
        self._dyn_rect.set_parent_size(*self.get_parent_size())
        return self._dyn_rect.get_rect(with_borders)

    def get_size(self, with_borders: bool = True) -> (int, int):
        return self.get_rect(with_borders).size

    def set_pos(self, **kwargs) -> None:
        self._dyn_rect.set_pos(**kwargs)

    def set_size(self, **kwargs) -> None:
        self._dyn_rect.set_size(**kwargs)

    def set_border(self, border_color: Color = None, **kwargs) -> None:
        self._dyn_rect.set_border(**kwargs)
        if border_color is not None:
            self.border_color = border_color
        self.set_changed()

    def get_surface(self, with_borders: bool = False) -> Surface:
        parent_surface = self.get_parent_surface()
        rect = self.get_rect(with_borders)
        return parent_surface.subsurface(rect)

    def compose(self, surface: Surface) -> bool:
        return False

    def compose_borders(self) -> bool:
        if self.border_color is None:
            return False
        surface = self.get_surface(with_borders=True)
        width, height = surface.get_size()

        drawn = False
        if self._dyn_rect.border_top > 0:
            draw.rect(surface=surface, color=self.border_color, rect=Rect(0, 0, width, self._dyn_rect.border_top))
            drawn = True

        if self._dyn_rect.border_left > 0:
            draw.rect(surface=surface, color=self.border_color, rect=Rect(0, 0, self._dyn_rect.border_left, height))
            drawn = True

        if self._dyn_rect.border_right > 0:
            draw.rect(surface=surface, color=self.border_color,
                      rect=Rect(width - self._dyn_rect.border_right, 0, self._dyn_rect.border_right, height))
            drawn = True

        if self._dyn_rect.border_bottom > 0:
            draw.rect(surface=surface, color=self.border_color,
                      rect=Rect(0, height - self._dyn_rect.border_bottom, width, self._dyn_rect.border_bottom))
            drawn = True
        return drawn

    def is_changed(self) -> bool:
        return self._is_changed

    def is_child_changed(self) -> bool:
        return self._child_changed

    def is_parent_changed(self) -> bool:
        parent_changed = self.parent_widget.is_changed() or self.parent_widget.is_parent_changed()
        if parent_changed is True:
            return parent_changed

        own_idx = self.parent_widget.widgets.index(self)
        for idx in range(0, own_idx):
            under_widget = self.parent_widget.widgets[idx]
            if under_widget.is_visible is True and under_widget.updated is True:
                if self.get_rect(with_borders=True).colliderect(under_widget.get_rect(with_borders=True)):
                    return True
        return False

    def set_changed(self) -> None:
        self._is_changed = True
        self._parent_surface = None
        if self.parent_widget is not None:
            self.parent_widget and self.parent_widget.set_child_changed()

    def set_child_changed(self) -> None:
        if self._child_changed is False:
            self._child_changed = True
            if self.parent_widget is not None:
                self.parent_widget.set_child_changed()

    def unset_changed(self) -> None:
        self._is_changed = False
        self._child_changed = False

    def set_focus(self, focus: bool = True) -> None:
        if focus is True:
            self.set_interactive(True)

        if self.is_focus != focus:
            if focus is True:
                self.parent_widget.set_focus(True)
                self.parent_widget.focus_child = self
                for widget in self.parent_widget.widgets:
                    if widget != self:
                        widget.set_focus(False)
            else:
                if self.parent_widget.focus_child == self:
                    self.parent_widget.focus_child = None
            self.is_focus = focus
            self.set_changed()

    def set_interactive(self, interactive: bool = True) -> None:
        if self.is_interactive != interactive:
            self.is_interactive = interactive
            if interactive is False:
                self.set_focus(False)

    def set_visible(self, visible: bool = True) -> None:
        self.is_visible = visible
        if visible is False:
            self.set_focus(False)
        self.set_changed()

    def draw(self) -> None:
        self.updated = False
        if self.is_visible is False:
            return

        if self.is_changed() is True or self.is_parent_changed():
            surface = self.get_surface(with_borders=False)
            if self.bg_color is not None:
                surface.fill(self.bg_color)
                self.set_changed()
            if self.compose(surface) is not False:
                self.set_changed()
            if self.compose_borders() is not False:
                self.set_changed()

        if self.widgets is not None and (self._child_changed is True or self.is_changed() or self.is_parent_changed()):
            for widget in self.widgets:
                widget.draw()
                if widget.updated is True:
                    self.updated = True

        if self.updated is True:
            self.unset_changed()

    def add_child(self, widget: UiWidget) -> None:
        widget.parent_widget = self
        if self.widgets is None:
            self.widgets = []
        self.widgets.append(widget)

    def remove_child(self, widget: UiWidget) -> None:
        widget.set_interactive(False)
        self.widgets.remove(widget)
        if len(self.widgets) == 0:
            self.widgets = None

    def get_widget_collide_point(self, widget: UiWidget, pos: (int, int)) -> (int, int):
        widget_rect = widget.get_rect(with_borders=True)
        if widget_rect.collidepoint(pos):
            widget_rect = widget.get_rect(with_borders=False)
            return pos[0] - widget_rect.x, pos[1] - widget_rect.y

    def get_child_by_pos(self, pos: (int, int)) -> (UiWidget, (int, int)):
        if self.widgets is None:
            return None, None

        for widget in reversed(self.widgets):
            if widget.is_visible is False:
                continue
            relative_pos = self.get_widget_collide_point(widget, pos)
            if relative_pos is not None:
                if widget.is_interactive is True:
                    return widget, relative_pos
                else:
                    return None, None
        return None, None

    def process_events(self, events: list, pos: (int, int) = None) -> None:
        if pos is not None:  # Pointed events
            pointed_widget, relative_pos = self.get_child_by_pos(pos)
            if pointed_widget is not None:
                for e in events:  # Select child if mouse buttons 1-3 is pressed
                    if e.type == constants.MOUSEBUTTONUP and e.button <= 3 and e.touch is False:
                        pointed_widget.set_focus()
                pointed_widget.process_events(events, relative_pos)

        else:  # Pointless events
            if self.focus_child is not None \
                    and self.focus_child.is_visible is True and self.focus_child.is_interactive is True:
                self.focus_child.process_events(events)

    def process_tick(self, milliseconds: float) -> None:
        if self.widgets is None:
            return
        for widget in self.widgets:
            widget.process_tick(milliseconds)
