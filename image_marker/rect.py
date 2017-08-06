import attr

from typing import Tuple

from image_marker.utils import contain


@attr.s
class Rectangle():
    x = attr.ib(default=0)
    y = attr.ib(default=0)
    w = attr.ib(default=0)
    h = attr.ib(default=0)

    def to_strings(self) -> Tuple[str, str, str, str]:
        return tuple(map(str, (self.x, self.y, self.w, self.h)))

    @classmethod
    def from_strings(cls, *args: str) -> 'Rectangle':
        return cls(*map(int, args))

    def normalize(self) -> 'Rectangle':
        vertex_1 = self.x, self.y
        vertex_2 = self.x + self.w, self.y + self.h
        self.x = min(vertex_1[0], vertex_2[0])
        self.y = min(vertex_1[1], vertex_2[1])
        self.w = abs(self.w)
        self.h = abs(self.h)
        return self

    def create_box(self, ratio: float) -> 'Rectangle':
        w, h = contain(self.w, self.h, ratio)
        return Rectangle(self.x, self.y, w, h)

    def shift(self, x: float, y: float) -> 'Rectangle':
        self.x = self.x + x
        self.y = self.y + y
        return self

    def from_top(self, height) -> 'Rectangle':
        self.y = height - self.y - self.h
        return self

    def from_bottom(self, height) -> 'Rectangle':
        self.y = height - self.h - self.y
        return self

    def scale(self, scale: float) -> 'Rectangle':
        for prop in ('x', 'y', 'w', 'h'):
            setattr(self, prop, round(getattr(self, prop) * scale))
        return self

    def limit(self, max_w: int, max_h: int) -> 'Rectangle':
        self.w = min(self.w, max_w)
        self.h = min(self.h, max_h)
        return self

    def center(self, rect: 'Rectangle') -> 'Rectangle':
        self.x = rect.x + rect.w / 2 - self.w / 2
        self.y = rect.y + rect.h / 2 - self.h / 2
        return self

    def move_inside(self, container: 'Rectangle') -> 'Rectangle':
        self.x = min(max(self.x, container.x),
                     container.x + container.w - self.w)
        self.y = min(max(self.y, container.y),
                     container.y + container.h - self.h)
        return self

    def pad_by_perc_w(self, pad_perc_w: float) -> 'Rectangle':
        pad_px = self.w * pad_perc_w * 2
        self.w = self.w + pad_px
        self.h = self.h + pad_px
        return self

    def copy(self):
        return Rectangle(self.x, self.y, self.w, self.h)
