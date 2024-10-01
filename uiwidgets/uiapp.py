import sys

import pygame

from controls import COMMAND_EVENT
from uiwidgets import UiWidget


class UiApp(UiWidget):
    def __init__(self, **kwargs):
        super().__init__(parent=None, **kwargs)
        self.is_interactive = True
        self.is_focus = True
        self._detached_surface = None
        self._detached_surface_changed = None
        self.screen_data = None
        self.init_display_settings()

    def init_display_settings(self):
        if self.screen_data is None:
            if "--fullscreen" in sys.argv or "-f" in sys.argv:
                flags = pygame.RESIZABLE + pygame.FULLSCREEN
                size = (0, 0)
            else:
                flags = pygame.RESIZABLE
                size = (1280, 720)
            self.screen_data = (size, flags)
        pygame.init()
        self._detached_surface = None
        self._detached_surface = pygame.display.set_mode(*self.screen_data)
        self.set_parent_surface(self)

    def set_parent_surface(self, parent: UiWidget) -> None:
        self._detached_surface_changed = True
        self._detached_surface = pygame.display.get_surface()
        self._dyn_rect.set_parent_size_by_surface(self._detached_surface)
        self.set_changed()

    def save_display_settings(self):
        flags = self._detached_surface.get_flags()
        size = self._detached_surface.get_size()
        self.screen_data = (size, flags)

    def get_parent_surface(self) -> pygame.Surface:
        return self._detached_surface

    def get_parent_size(self) -> (int, int):
        return self._detached_surface.get_size()

    def is_parent_changed(self) -> bool:
        return self._detached_surface_changed

    def set_changed(self) -> None:
        super().set_changed()
        self._detached_surface_changed = True

    def unset_changed(self) -> None:
        super().unset_changed()
        self._detached_surface_changed = False

    def process_events(self, events: list, pos: (int, int) = None) -> bool:
        for e in events:
            if e.type in (pygame.WINDOWSIZECHANGED, pygame.WINDOWRESTORED):
                self.set_changed()
                return True
            elif e.type == pygame.QUIT or (e.type == COMMAND_EVENT and e.command == "EXIT"):
                return False
            elif pos is None and e.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
                pos = tuple(e.pos)
        super().process_events(events, pos)

    def draw(self, force: bool = False) -> bool:
        if super().draw(force) is True:
            pygame.display.flip()
            return True

    def set_focus(self, focus: bool = True) -> None:
        return
