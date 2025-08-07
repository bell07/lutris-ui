from __future__ import annotations

from pygame import Color, Rect, Surface, constants, draw, event

from .dynamicrect import DynamicTypes
from .uiwidget import UiWidget


class UiWidgetsScrollbar(UiWidget):
    def __init__(
        self,
        parent: UiWidget,
        scrollbar_is_horizontal: bool,
        scrollbar_width: int = 20,
        scrollbar_color=Color("Red"),
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.scrollbar_is_horizontal: bool = scrollbar_is_horizontal
        self.scrollbar_width: int = scrollbar_width
        self.scrollbar_color: Color = scrollbar_color
        if scrollbar_is_horizontal:
            self._dyn_rect.set_pos(
                pos_x=0, pos_y_type=DynamicTypes.TYPE_PIXEL_REVERSE, pos_y=0
            )
            self._dyn_rect.set_size(size_h=self.scrollbar_width)
        else:
            self._dyn_rect.set_pos(
                pos_x_type=DynamicTypes.TYPE_PIXEL_REVERSE, pos_x=0, pos_y=0
            )
            self._dyn_rect.set_size(size_w=self.scrollbar_width)
        self.current_value: int = 0
        self.bar_value: int = 0
        self.max_value: int = 0
        self._drag_pos: tuple[int, int] | None = None

    def adjust_scrollbar_by_viewport(self):
        assert isinstance(self.parent_widget, UiWidgetViewportContainer)
        viewport_widget = self.parent_widget.viewport_widget
        assert viewport_widget
        viewport_width, viewport_height = viewport_widget.get_size(with_borders=True)
        window_width, window_height = self.get_parent_size()

        if self.scrollbar_is_horizontal is True:
            if (
                self.bar_value != window_width
                or self.max_value != viewport_width
                or self.current_value != viewport_widget.shift_x
            ):
                self.bar_value = window_width
                self.max_value = viewport_width
                self.current_value = viewport_widget.shift_x
                self.set_changed()
        else:
            if (
                self.bar_value != window_height
                or self.max_value != viewport_height
                or self.current_value != viewport_widget.shift_y
            ):
                self.bar_value = window_height
                self.max_value = viewport_height
                self.current_value = viewport_widget.shift_y
                self.set_changed()

        if self.is_changed() is True:
            if self.bar_value >= self.max_value:
                self.set_visible(False)
            else:
                self.set_visible()

    def draw(self) -> None:
        assert isinstance(self.parent_widget, UiWidgetViewportContainer)
        assert self.parent_widget.viewport_widget
        if self.parent_widget.viewport_widget.updated:
            self.adjust_scrollbar_by_viewport()
        super().draw()

    def compose(self, surface: Surface) -> bool:
        scrollbar_width, scrollbar_height = self.get_size(with_borders=False)

        if self.scrollbar_is_horizontal is True:
            scrollbar_x = self.current_value * scrollbar_width / self.max_value
            scrollbar_w = self.bar_value * scrollbar_width / self.max_value
            draw.rect(
                surface,
                self.scrollbar_color,
                (scrollbar_x, 0, scrollbar_w, self.scrollbar_width),
                border_radius=int(self.scrollbar_width / 2),
            )
        else:
            scrollbar_y = self.current_value * scrollbar_height / self.max_value
            scrollbar_h = self.bar_value * scrollbar_height / self.max_value
            draw.rect(
                surface,
                self.scrollbar_color,
                (0, scrollbar_y, self.scrollbar_width, scrollbar_h),
                border_radius=int(self.scrollbar_width / 2),
            )
        return True

    def process_event_pos(self, event: event.Event, pos: tuple[int, int]) -> bool:
        match event.type:
            case constants.MOUSEBUTTONDOWN:
                if constants.BUTTON_LEFT == event.button:
                    self._drag_pos = event.pos
            case constants.MOUSEBUTTONUP:
                if constants.BUTTON_LEFT == event.button:
                    self._drag_pos = None
            case constants.MOUSEMOTION:
                if constants.BUTTON_LEFT in event.buttons:
                    if self._drag_pos is not None:
                        assert isinstance(self.parent_widget, UiWidgetViewportContainer)
                        viewport_widget = self.parent_widget.viewport_widget
                        assert viewport_widget
                        if self.scrollbar_is_horizontal is True:
                            viewport_widget.shift_x += (
                                (event.pos[0] - self._drag_pos[0])
                                * self.max_value
                                / self.bar_value
                            )
                        else:
                            viewport_widget.shift_y += (
                                (event.pos[1] - self._drag_pos[1])
                                * self.max_value
                                / self.bar_value
                            )
                        viewport_widget.set_changed()
                    self._drag_pos = event.pos
                    return True
        return False


class UiWidgetViewport(UiWidget):
    def __init__(self, parent: UiWidget, **kwargs):
        super().__init__(parent, **kwargs)
        self.shift_x = 0
        self.shift_y = 0
        self._old_shift_x: int = 0
        self._old_shift_y: int = 0
        self.viewport_width: int = 0
        self.viewport_height: int = 0
        self._viewport_surface: Surface | None = None

    def set_size(self, **kwargs) -> None:
        w, h = kwargs["size_w"], kwargs["size_h"]
        parent_width, parent_height = self.get_parent_size()
        width_with_border = w + self._dyn_rect.border_left + self._dyn_rect.border_right
        if width_with_border < parent_width:
            width_with_border = parent_width
        height_with_border = (
            h + self._dyn_rect.border_top + self._dyn_rect.border_bottom
        )
        if height_with_border < parent_height:
            height_with_border = parent_height

        if (
            self.viewport_width != width_with_border
            or self.viewport_height != height_with_border
        ):
            self.viewport_width = width_with_border
            self.viewport_height = height_with_border
            self.set_changed()

    def get_surface(self, with_borders: bool = False) -> Surface:
        size = self.get_size(with_borders)
        if with_borders is True:
            pos = (0, 0)
        else:
            pos = (self._dyn_rect.border_left, self._dyn_rect.border_top)
        assert self._viewport_surface
        return self._viewport_surface.subsurface(Rect(pos, size))

    def get_rect(self, with_borders: bool = False) -> Rect:
        parent_width, parent_height = self.get_parent_size()
        if self.viewport_width is None or self.viewport_height is None:
            if self.viewport_width is None:
                self.viewport_width = parent_width
            if self.viewport_height is None:
                self.viewport_height = parent_height
        if (
            self._viewport_surface is None
            or self._viewport_surface.get_width() != self.viewport_width
            or self._viewport_surface.get_height() != self.viewport_height
        ):
            self._viewport_surface = Surface(
                (self.viewport_width, self.viewport_height)
            )
            self.set_changed()
        self._dyn_rect.set_parent_size(self.viewport_width, self.viewport_height)
        return self._dyn_rect.get_rect(with_borders)

    def adjust_shift(self):
        # Adjust shift
        shift_changed = False
        parent_width, parent_height = self.get_parent_size()
        if self.viewport_width < self.shift_x + parent_width:
            self.shift_x = self.viewport_width - parent_width

        if self.viewport_height < self.shift_y + parent_height:
            self.shift_y = self.viewport_height - parent_height

        if self.shift_x < 0:
            self.shift_x = 0

        if self.shift_y < 0:
            self.shift_y = 0

        if self.shift_x != self._old_shift_x or self.shift_y != self._old_shift_y:
            shift_changed = True
            self._old_shift_x = self.shift_x
            self._old_shift_y = self.shift_y
        return shift_changed

    def draw(self) -> None:
        self.updated = False
        if self.is_visible is False:
            return

        if self.adjust_shift():
            self.set_changed()

        super().draw()
        if self.updated:
            parent_surface = self.get_parent_surface()
            parent_width, parent_height = self.get_parent_size()
            assert self._viewport_surface
            widget_surface = self._viewport_surface.subsurface(
                (self.shift_x, self.shift_y, parent_width, parent_height)
            )
            parent_surface.blit(widget_surface, (0, 0))
            self.unset_changed()

    def get_widget_collide_point(
        self, widget: UiWidget, pos: tuple[int, int]
    ) -> tuple[int, int] | None:
        pos_x, pos_y = pos
        shift_pos = (pos_x + self.shift_x, pos_y + self.shift_y)
        widget_rect = widget.get_rect(with_borders=False)
        if widget_rect.collidepoint(shift_pos):
            return shift_pos[0] - widget_rect.x, shift_pos[1] - widget_rect.y

    def process_event_pos(self, event: event.Event, pos: tuple[int, int]) -> bool:
        if event.type == constants.MOUSEMOTION and event.touch is True:
            self.shift_x = self.shift_x + (event.rel[0] * 5)
            self.shift_y = self.shift_y - (event.rel[1] * 5)
            self.set_changed()
            return True

        return super().process_event_pos(event, pos)


class UiWidgetViewportContainer(UiWidget):
    def __init__(self, parent: UiWidget, **kwargs):
        super().__init__(parent, **kwargs)
        self.viewport_widget = None
        self.vertical_scrollbar_widget = UiWidgetsScrollbar(
            self, scrollbar_is_horizontal=False
        )
        self.horizontal_scrollbar_widget = UiWidgetsScrollbar(
            self, scrollbar_is_horizontal=True
        )

    def set_viewport_widget(self, widget: UiWidgetViewport):
        self.viewport_widget = widget
        # Move viewport on top
        assert self.widgets
        self.widgets.remove(widget)
        self.widgets.insert(0, widget)
        self.vertical_scrollbar_widget.adjust_scrollbar_by_viewport()
        self.horizontal_scrollbar_widget.adjust_scrollbar_by_viewport()
