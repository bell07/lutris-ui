import pygame

from controls import COMMAND_EVENT
from uiwidgets import UiWidget


class UiApp(UiWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.is_interactive = True
        self.is_focus = True
        self._detached_surface = None
        self._detached_surface_changed = None
        self.set_parent_surface(None)

    def set_parent_surface(self, _) -> None:
        self._detached_surface = pygame.display.get_surface()
        self._detached_surface_changed = True
        self._dyn_rect.set_parent_size_by_surface(self._detached_surface)

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
            if e.type == pygame.VIDEORESIZE or e.type == pygame.WINDOWSIZECHANGED:
                self.set_changed()
                self.draw(force=True)
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
