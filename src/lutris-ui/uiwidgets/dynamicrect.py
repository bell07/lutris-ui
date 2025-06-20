from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import Rect

if TYPE_CHECKING:
    from pygame import Surface


class DynamicTypes:
    TYPE_PIXEL = 1
    TYPE_PIXEL_REVERSE = 2
    TYPE_PERCENT = 3
    TYPE_CENTER = 4


class DynamicRect:
    def __init__(
        self,
        parent_w: int | None = None,
        parent_h: int | None = None,
        pos_x_type: int = DynamicTypes.TYPE_PIXEL,
        pos_x: int = 0,
        pos_y_type: int = DynamicTypes.TYPE_PIXEL,
        pos_y: int = 0,
        size_w_type: int | None = None,
        size_w: int | None = None,
        size_h_type: int | None = None,
        size_h: int | None = None,
        border_all: int | None = None,
        border_top: int | None = None,
        border_bottom: int | None = None,
        border_left: int | None = None,
        border_right: int | None = None,
    ):
        self.parent_w: int = parent_w or 0
        self.parent_h: int = parent_h or 0
        self.pos_x_type = pos_x_type
        self.pos_x = pos_x
        self.pos_y_type = pos_y_type
        self.pos_y = pos_y

        self.size_w_type: int
        self.size_w: int
        self.size_h_type: int
        self.size_h: int

        self.border_top: int = 0
        self.border_bottom: int = 0
        self.border_left: int = 0
        self.border_right: int = 0
        self.set_border(
            border_all=border_all,
            border_top=border_top,
            border_bottom=border_bottom,
            border_left=border_left,
            border_right=border_right,
        )

        self.set_size(size_w_type, size_w, size_h_type, size_h)
        if size_w is None:
            self.size_w_type = DynamicTypes.TYPE_PERCENT
            self.size_w = 100

        if size_h is None:
            self.size_h_type = DynamicTypes.TYPE_PERCENT
            self.size_h = 100

        self.changed = True
        self._rect: Rect | None = None
        self._rect_with_borders: Rect | None = None

    def set_parent_size(
        self, parent_w: int | None = None, parent_h: int | None = None
    ) -> None:
        if parent_w is not None and parent_w != self.parent_w:
            self.parent_w = parent_w
            self.changed = True
        if parent_h is not None and parent_h != self.parent_h:
            self.parent_h = parent_h
            self.changed = True

    def set_parent_size_by_surface(self, parent_surface: Surface) -> None:
        self.set_parent_size(*parent_surface.get_size())

    def set_pos(
        self,
        pos_x_type: int | None = None,
        pos_x: int | None = None,
        pos_y_type: int | None = None,
        pos_y: int | None = None,
    ) -> None:
        if pos_x is not None:
            self.pos_x_type = pos_x_type or DynamicTypes.TYPE_PIXEL
            self.pos_x = pos_x
        if pos_y is not None:
            self.pos_y_type = pos_y_type or DynamicTypes.TYPE_PIXEL
            self.pos_y = pos_y
        self.changed = True

    def set_size(self, size_w_type=None, size_w=None, size_h_type=None, size_h=None):
        if size_w is not None:
            self.size_w_type = size_w_type or DynamicTypes.TYPE_PIXEL
            self.size_w = size_w
        if size_h is not None:
            self.size_h_type = size_h_type or DynamicTypes.TYPE_PIXEL
            self.size_h = size_h
        self.changed = True

    def set_border(
        self,
        border_all: int | None = None,
        border_top: int | None = None,
        border_bottom: int | None = None,
        border_left: int | None = None,
        border_right: int | None = None,
    ) -> None:
        if border_all is not None:
            self.border_top = border_all
            self.border_bottom = border_all
            self.border_left = border_all
            self.border_right = border_all

        if border_top is not None:
            self.border_top = border_top
        if border_bottom is not None:
            self.border_bottom = border_bottom
        if border_left is not None:
            self.border_left = border_left
        if border_right is not None:
            self.border_right = border_right
        self.changed = True

    def get_size(self, with_borders: bool = False) -> tuple[int, int]:
        rect = self.get_rect(with_borders)
        return rect.w, rect.h

    def get_rect(self, with_borders: bool = False) -> Rect:
        if self.changed is False:
            if with_borders is True and self._rect_with_borders:
                return self._rect_with_borders
            elif with_borders is False and self._rect:
                return self._rect

        w: int = 0
        h: int = 0
        x: int = 0
        y: int = 0

        assert (
            self.parent_w is not None and self.parent_h is not None
        ), "Parent size required for rect calculations"
        assert (
            self.size_w_type != DynamicTypes.TYPE_CENTER
            and self.size_h_type != DynamicTypes.TYPE_CENTER
        ), "TYPE_CENTER not supported for size"
        max_w = self.parent_w
        max_h = self.parent_h

        match self.size_w_type:
            case DynamicTypes.TYPE_PIXEL:
                w = self.size_w
            case DynamicTypes.TYPE_PIXEL_REVERSE:
                w = max_w - self.size_w
            case DynamicTypes.TYPE_PERCENT:
                w = round(max_w * self.size_w / 100)

        if w < 0:
            w = 0
        if w > max_w:
            w = max_w

        match self.size_h_type:
            case DynamicTypes.TYPE_PIXEL:
                h = self.size_h
            case DynamicTypes.TYPE_PIXEL_REVERSE:
                h = max_h - self.size_h
            case DynamicTypes.TYPE_PERCENT:
                h = round(max_h * self.size_h / 100)
        if h < 0:
            h = 0
        if h > max_h:
            h = max_h

        match self.pos_x_type:
            case DynamicTypes.TYPE_PIXEL:
                x = self.pos_x
            case DynamicTypes.TYPE_PIXEL_REVERSE:
                x = self.parent_w - w - self.pos_x
            case DynamicTypes.TYPE_PERCENT:
                x = round((max_w - w) * self.pos_x / 100)
            case DynamicTypes.TYPE_CENTER:
                x = round((max_w - w) / 2)
        if x < 0:
            x = 0
        if x > self.parent_w - w:
            x = self.parent_w - w

        match self.pos_y_type:
            case DynamicTypes.TYPE_PIXEL:
                y = self.pos_y
            case DynamicTypes.TYPE_PIXEL_REVERSE:
                y = self.parent_h - h - self.pos_y
            case DynamicTypes.TYPE_PERCENT:
                y = round((max_h - h) * self.pos_y / 100)
            case DynamicTypes.TYPE_CENTER:
                y = round((max_h - h) / 2)
        if y < 0:
            y = 0
        if y > self.parent_h - h:
            y = self.parent_h - h

        self._rect_with_borders = Rect(x, y, w, h)

        x += self.border_left
        if x > max_w:
            x = max_w

        y += self.border_top
        if y > max_h:
            y = max_h

        w = w - self.border_left - self.border_right
        if w < 0:
            w = 0

        h = h - self.border_top - self.border_bottom
        if h < 0:
            h = 0

        self._rect = Rect(x, y, w, h)
        self.changed = False
        if with_borders is True:
            return self._rect_with_borders
        else:
            return self._rect
