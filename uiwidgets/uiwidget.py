# import pygame
from pygame import constants
from pygame.event import Event

from uiwidgets import DynamicRect


class UiWidget:
    def __init__(self, parent, **kwargs):
        self.parent_widget = None
        self._parent_surface = None
        self._dyn_rect = DynamicRect(**kwargs)
        self._is_changed = True
        self._child_changed = True

        self.is_visible = True
        self.is_interactive = True
        self.is_focus = False

        self.widgets = []
        self.selected_widget = None

        self._detached_surface = None
        self.detached_surface_changed = None
        self.set_parent_surface(parent)

    def set_parent_surface(self, parent):
        if isinstance(parent, UiWidget):  # Check if UiWidget compatible object
            self.parent_widget = parent
            parent.add_child(self)
            self._dyn_rect.set_parent_size_by_surface(parent.get_surface())
            self._detached_surface = None
            self.detached_surface_changed = None
        else:
            self._detached_surface = parent
            self.detached_surface_changed = True
            self._dyn_rect.set_parent_size_by_surface(parent)
        self._parent_surface = None

    def get_parent_surface(self):
        if self._parent_surface is not None and self.is_parent_changed() is False:
            return self._parent_surface

        if self._detached_surface is None:
            self._parent_surface = self.parent_widget.get_surface()
        else:
            self._parent_surface = self._detached_surface

        return self._parent_surface

    def get_parent_size(self):
        if self._detached_surface is None:
            return self.parent_widget.get_size()
        else:
            return self._detached_surface.get_size()

    def get_rect(self):
        if self.is_parent_changed() is True:
            self._dyn_rect.set_parent_size(*self.get_parent_size())
        return self._dyn_rect.get_rect()

    def get_size(self):
        return self.get_rect().size

    def set_pos(self, **kwargs):
        self._dyn_rect.set_pos(**kwargs)

    def set_size(self, **kwargs):
        self._dyn_rect.set_size(**kwargs)

    def get_surface(self):
        parent_surface = self.get_parent_surface()
        rect = self.get_rect()
        return parent_surface.subsurface(rect)

    def compose(self, surface):
        return False

    def compose_to_parent(self, surface):
        return False

    def is_changed(self):
        return self._is_changed is True

    def is_parent_changed(self):
        if self._detached_surface is None:
            return self.parent_widget.is_changed() is True
        else:
            return self.detached_surface_changed

    def set_changed(self):
        self._is_changed = True
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
        self.detached_surface_changed = False

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

    def get_widget_collide_point(self, widget, pos):
        widget_rect = widget.get_rect()
        if widget_rect.collidepoint(pos):
            return pos[0] - widget_rect.x, pos[1] - widget_rect.y

    def get_child_by_pos(self, pos):
        if self.get_rect().collidepoint(pos) is False:
            return
        for widget in self.widgets:
            if widget.is_interactive is True:
                if self.get_widget_collide_point(widget, pos):
                    return widget

    def process_events(self, events):
        for e in events:
            match e.type:
                case constants.MOUSEBUTTONUP:
                    if e.button <= 3 and e.touch is False:  # 4 and 5 are wheel
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
                    widget_point = self.get_widget_collide_point(widget, e.pos)
                    if widget_point:
                        event_data = e.dict.copy()
                        event_data["pos"] = widget_point
                        widget_event = Event(e.type, event_data)
                        widget_events.append(widget_event)  # Position inside the widget. Pass event
                elif widget.is_focus is True:
                    widget_events.append(e)  # Position-less events to widget with focus only

            widget.process_events(widget_events)
