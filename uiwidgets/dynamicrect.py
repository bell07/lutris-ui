from pygame import Rect, Surface


class DynamicTypes:
    TYPE_PIXEL = 1
    TYPE_PERCENT = 2
    TYPE_CENTER = 3


class DynamicRect:
    def __init__(self, parent_w: float = None, parent_h: float = None, pos_x_type: int = DynamicTypes.TYPE_PIXEL,
                 pos_x: float = 0, pos_y_type: int = DynamicTypes.TYPE_PIXEL, pos_y: float = 0, size_w_type: int = None,
                 size_w: float = None, size_h_type: int = None, size_h: float = None, border_top: float = 0,
                 border_all: float = None, border_bottom: float = 0, border_left: float = 0, border_right: float = 0):
        self.parent_w = parent_w
        self.parent_h = parent_h
        self.pos_x_type = pos_x_type
        self.pos_x = pos_x
        self.pos_y_type = pos_y_type
        self.pos_y = pos_y

        self.size_w_type = None
        self.size_w = None
        self.size_h_type = None
        self.size_h = None

        self.border_top = None
        self.border_bottom = None
        self.border_left = None
        self.border_right = None
        self.set_border(border_all=border_all, border_top=border_top, border_bottom=border_bottom,
                        border_left=border_left, border_right=border_right)

        self.set_size(size_w_type, size_w, size_h_type, size_h)
        if self.size_w is None:
            self.size_w_type = DynamicTypes.TYPE_PERCENT
            self.size_w = 100

        if self.size_h is None:
            self.size_h_type = DynamicTypes.TYPE_PERCENT
            self.size_h = 100

        self.changed = True
        self._rect = None

    def set_parent_size(self, parent_w: float = None, parent_h: float = None) -> None:
        if parent_w is not None and parent_w != self.parent_w:
            self.parent_w = parent_w
            self.changed = True
        if parent_h is not None and parent_h != self.parent_h:
            self.parent_h = parent_h
            self.changed = True

    def set_pos(self, pos_x_type: int = None, pos_x: float = None, pos_y_type: int = None, pos_y: float = None) -> None:
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

    def set_parent_size_by_surface(self, parent_surface: Surface) -> None:
        self.set_parent_size(*parent_surface.get_size())

    def set_border(self, border_all: float = None, border_top: float = None, border_bottom: float = None,
                   border_left: float = None, border_right: float = None) -> None:
        if border_all is not None:
            self.border_top = border_all
            self.border_bottom = border_all
            self.border_left = border_all
            self.border_right = border_all
        else:
            if border_top is not None:
                self.border_top = border_top
            if border_bottom is not None:
                self.border_bottom = border_bottom
            if border_left is not None:
                self.border_left = border_left
            if border_right is not None:
                self.border_right = border_right
        self.changed = True

    def get_size(self) -> (int, int):
        rect = self.get_rect()
        return rect.w, rect.h

    def get_rect(self) -> Rect:
        if self._rect is not None and self.changed is False:
            return self._rect
        w, h, x, y = 0, 0, 0, 0
        assert self.parent_w is not None and self.parent_h is not None, "Parent size required for rect calculations"
        assert self.size_w_type != DynamicTypes.TYPE_CENTER and self.size_h_type != DynamicTypes.TYPE_CENTER, "TYPE_CENTER not supported for size"
        max_w = self.parent_w - self.border_left - self.border_right
        max_h = self.parent_h - self.border_top - self.border_bottom

        match self.size_w_type:
            case DynamicTypes.TYPE_PIXEL:
                if self.size_w < 0:
                    w = max_w + self.size_w
                else:
                    w = self.size_w - self.border_left - self.border_right
                    if w < 0:
                        w = 0
            case DynamicTypes.TYPE_PERCENT:
                w = max_w * self.size_w / 100

        if w < 0:
            w = 0
        if w > max_w:
            w = max_w

        match self.size_h_type:
            case DynamicTypes.TYPE_PIXEL:
                if self.size_h < 0:
                    h = max_h + self.size_h
                else:
                    h = self.size_h - self.border_top - self.border_bottom
                    if h < 0:
                        h = 0
            case DynamicTypes.TYPE_PERCENT:
                h = max_h * self.size_h / 100
        if h < 0:
            h = 0
        if h > max_h:
            h = max_h

        match self.pos_x_type:
            case DynamicTypes.TYPE_PIXEL:
                if self.pos_x < 0:
                    x = self.parent_w - self.border_right - w + self.pos_x
                else:
                    x = self.pos_x + self.border_left
            case DynamicTypes.TYPE_PERCENT:
                x = (max_w - w) * self.pos_x / 100 + self.border_left
            case DynamicTypes.TYPE_CENTER:
                x = (max_w - w) / 2 + self.border_left
        if x < 0:
            x = 0
        if x > self.parent_w - self.border_right - w:
            x = self.parent_w - self.border_right - w

        match self.pos_y_type:
            case DynamicTypes.TYPE_PIXEL:
                if self.pos_y < 0:
                    y = self.parent_h - self.border_bottom - h + self.pos_y
                else:
                    y = self.pos_y + self.border_top
            case DynamicTypes.TYPE_PERCENT:
                y = (max_h - h) * self.pos_y / 100 + self.border_top
            case DynamicTypes.TYPE_CENTER:
                y = (max_h - h) / 2 + self.border_top
        if y < 0:
            y = 0
        if y > self.parent_h - self.border_bottom - h:
            y = self.parent_h - self.border_bottom - h

        self._rect = Rect(x, y, w, h)
        self.changed = False
        return self._rect

    def get_border(self, border_type: str) -> Rect:
        draw_rect = self.get_rect()
        match border_type:
            case 'left':
                return Rect(draw_rect.x - self.border_left, draw_rect.y - self.border_top, self.border_left,
                            self.border_top + draw_rect.height + self.border_bottom)
            case 'right':
                return Rect(draw_rect.x + draw_rect.width, draw_rect.y - self.border_top, self.border_right,
                            self.border_top + draw_rect.height + self.border_bottom)
            case 'top':
                return Rect(draw_rect.x - self.border_left, draw_rect.y - self.border_top,
                            self.border_left + draw_rect.width + self.border_right, self.border_top)
            case 'bottom':
                return Rect(draw_rect.x - self.border_left, draw_rect.y + draw_rect.height,
                            self.border_left + draw_rect.width + self.border_right, self.border_bottom)
