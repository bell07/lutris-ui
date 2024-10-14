# import pygame
from __future__ import annotations

from pygame import Surface, Rect, Color
from pygame import constants, draw

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

        self.widgets = None
        self.focus_child = None
        self.bg_color = bg_color
        self.border_color = border_color

        parent and self.set_parent_surface(parent)

    def set_parent_surface(self, parent: UiWidget) -> None:
        self.parent_widget = parent
        parent.add_child(self)
        self._dyn_rect.set_parent_size_by_surface(parent.get_surface())
        self._parent_surface = None

    def get_parent_surface(self) -> Surface:
        if self._parent_surface is None or self.is_parent_changed() is True:
            self._parent_surface = self.parent_widget.get_surface()
        return self._parent_surface

    def get_parent_size(self) -> (int, int):
        return self.parent_widget.get_size()

    def get_rect(self) -> Rect:
        self._dyn_rect.set_parent_size(*self.get_parent_size())
        return self._dyn_rect.get_rect()

    def get_size(self) -> (int, int):
        return self.get_rect().size

    def set_pos(self, **kwargs) -> None:
        self._dyn_rect.set_pos(**kwargs)

    def set_size(self, **kwargs) -> None:
        self._dyn_rect.set_size(**kwargs)

    def set_border(self, border_color: Color = None, **kwargs) -> None:
        self._dyn_rect.set_border(**kwargs)
        if border_color is not None:
            self.border_color = border_color
        self.set_changed()

    def get_surface(self) -> Surface:
        parent_surface = self.get_parent_surface()
        rect = self.get_rect()
        return parent_surface.subsurface(rect)

    def compose(self, surface: Surface) -> bool:
        return False

    def compose_to_parent(self, surface: Surface, rect: Rect) -> bool:
        return False

    def compose_borders(self, surface: Surface) -> bool:
        if self.border_color is None:
            return False
        draw.rect(surface=surface, color=self.border_color, rect=self._dyn_rect.get_border("top"))
        draw.rect(surface=surface, color=self.border_color, rect=self._dyn_rect.get_border("bottom"))
        draw.rect(surface=surface, color=self.border_color, rect=self._dyn_rect.get_border("left"))
        draw.rect(surface=surface, color=self.border_color, rect=self._dyn_rect.get_border("right"))
        return True

    def is_changed(self) -> bool:
        return self._is_changed

    def is_parent_changed(self) -> bool:
        return self.parent_widget.is_changed()

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
        self.is_interactive = interactive
        if interactive is False:
            self.set_focus(False)
        self.set_changed()

    def set_visible(self, visible: bool = True) -> None:
        self.is_visible = visible
        if visible is False:
            self.set_focus(False)
        self.set_changed()

    def draw(self, force: bool = False) -> bool:
        if self.is_visible is False:
            return False

        if force is True:
            self.set_changed()

        updated = False
        if self.is_changed() is True or self.is_parent_changed():
            parent_surface = self.get_parent_surface()
            if self.compose_to_parent(parent_surface, self.get_rect()) is not False:
                self.set_changed()
            if self.compose_borders(parent_surface) is not False:
                self.set_changed()

            surface = self.get_surface()
            if self.bg_color is not None:
                surface.fill(self.bg_color)
                self.set_changed()
            if self.compose(surface) is not False:
                self.set_changed()

        if self.widgets is not None and (self._child_changed is True or self.is_changed()):
            for widget in self.widgets:
                widget.draw(force)
            updated = True

        self.unset_changed()
        return updated

    def add_child(self, widget: UiWidget) -> None:
        widget.parent_widget = self
        if self.widgets is None:
            self.widgets = []
        self.widgets.append(widget)

    def remove_child(self, widget: UiWidget) -> None:
        self.widgets.remove(widget)
        if len(self.widgets) == 0:
            self.widgets = None

    def get_widget_collide_point(self, widget: UiWidget, pos: (int, int)) -> (int, int):
        widget_rect = widget.get_rect()
        if widget_rect.collidepoint(pos):
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
