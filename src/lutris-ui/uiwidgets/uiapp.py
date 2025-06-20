from __future__ import annotations

from pygame import constants, display, event, font
from pygame import quit as pygame_quit
from pygame import Surface

from .controls import Controls
from .uiwidget import UiWidget


class UiApp(UiWidget):
    def __init__(
        self,
        controls: Controls,
        size_w: int = 0,
        size_h: int = 0,
        fullscreen: bool = False,
        noframe: bool = False,
        **kwargs,
    ):
        # noinspection PyArgumentEqualDefault
        super().__init__(parent=None, **kwargs)
        self.controls = controls
        self.is_interactive = True
        self.is_focus = True
        self._detached_surface: Surface
        self._detached_surface_changed = False
        self.size_w = size_w
        self.size_h = size_h
        self.fullscreen = fullscreen
        self.noframe = noframe
        self.init_display_settings(reset=True)
        event.set_blocked(None)
        event.set_allowed(controls.allowed_event_types)
        self.exit_loop = False

    def init_display_settings(self, reset: bool = False) -> None:
        display.init()
        font.init()
        if self.fullscreen is True:
            flags = constants.RESIZABLE + constants.FULLSCREEN
            size = (0, 0)
        else:
            if self.noframe is True:
                flags = constants.RESIZABLE + constants.NOFRAME
            else:
                flags = constants.RESIZABLE
            if reset is False:
                self.size_w, self.size_h = self._detached_surface.get_size()
            if self.size_w == 0 or self.size_w == 0 or reset is True:
                display_info = display.Info()
                if self.size_w == 0:
                    self.size_w = display_info.current_w
                if self.size_h == 0:
                    self.size_h = display_info.current_h
            size = (self.size_w, self.size_h)

        self._detached_surface = display.set_mode(size, flags)
        self.set_parent_surface(self)

    def set_parent_surface(self, parent: UiWidget) -> None:
        self._detached_surface_changed = True
        self._detached_surface = display.get_surface()
        self._dyn_rect.set_parent_size_by_surface(self._detached_surface)
        self.set_changed()

    def get_parent_surface(self) -> Surface:
        assert self._detached_surface
        return self._detached_surface

    def get_parent_size(self) -> tuple[int, int]:
        assert self._detached_surface
        return self._detached_surface.get_size()

    def is_parent_changed(self) -> bool:
        return self._detached_surface_changed

    def set_changed(self) -> None:
        super().set_changed()
        self._detached_surface_changed = True

    def unset_changed(self) -> None:
        super().unset_changed()
        self._detached_surface_changed = False

    def process_event_focus(self, event: event.Event) -> bool:
        event_done = super().process_event_focus(event)
        if event_done is True:
            return True

        if event.type in (constants.WINDOWSIZECHANGED, constants.WINDOWRESTORED):
            self.set_changed()
            return True
        elif event.type == constants.QUIT or (
            event.type == Controls.COMMAND_EVENT and event.command == "EXIT"
        ):
            self.exit_loop = True
            return True
        return False

    def process_events(self, events: list) -> None:
        if not events:
            return

        for e in events:
            if e.type in (
                constants.MOUSEMOTION,
                constants.MOUSEBUTTONUP,
                constants.MOUSEBUTTONDOWN,
            ):
                if self.process_event_pos(e, e.pos) is True:
                    break
            else:
                if self.process_event_focus(e) is True:
                    break

    def draw(self) -> None:
        super().draw()
        if self.updated is True:
            display.flip()

    def set_focus(self, focus: bool = True) -> None:
        return

    def run(self):
        while True:
            self.controls.update_controls()
            self.process_tick()
            if self.exit_loop is True:
                break
            self.process_events(self.controls.events)
            if self.exit_loop is True:
                break
            self.draw()
            self.controls.game_tick()
        pygame_quit()
