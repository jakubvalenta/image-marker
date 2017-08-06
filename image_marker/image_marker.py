import attr
import sys

import pyglet
from pyglet.window import key, mouse, Window

from typing import Callable, Dict, List

from image_marker import gl
from image_marker.utils import fit
from image_marker.rect import Rectangle


@attr.s
class Mark():
    rect = attr.ib(default=None)
    box = attr.ib(default=None)
    note = attr.ib(default='')


TPath = str
TMarks = Dict[TPath, Mark]


@attr.s
class Selection(Rectangle):
    box_ratio = attr.ib(default=0)
    box_pad_perc_w = attr.ib(default=0)

    def to_px(self, window: Window) -> 'Selection':
        return window.rect_rel_to_image(self)

    def from_px(self, rect: Rectangle, window: Window):
        new = window.rect_rel_to_window(rect)
        self.x = new.x
        self.y = new.y
        self.w = new.w
        self.h = new.h

    def to_box(self, window: Window) -> 'Selection':
        if self.box_ratio:
            return window.rect_to_box(
                self, self.box_ratio, self.box_pad_perc_w)
        return self

    def to_box_px(self, window: Window) -> 'Selection':
        return window.rect_rel_to_image(self.to_box(window))

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.x = x
            self.y = y
            self.w = 0
            self.h = 0

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT:
            self.w += dx
            self.h += dy

    def draw(self, window: Window):
        if self.w and self.h:
            gl.draw_rect(self)
            if self.box_ratio:
                gl.draw_rect(self.to_box(window), gl.COLOR_GREEN)


class ImageMarker(Window):
    images = None
    marks = None
    callback = None
    box_ratio = None
    box_pad_perc_w = None
    verbose = None

    cursor = 0
    current_image = None
    current_mark = None

    def __init__(self,
                 images: List[TPath],
                 marks: TMarks,
                 callback: Callable[[TPath, Rectangle, Rectangle], None],
                 box_ratio: float,
                 box_pad_perc_w: float,
                 verbose: bool,
                 *args,
                 **kwargs):
        self.images = images
        self.marks = marks
        self.callback = callback
        self.box_ratio = box_ratio
        self.box_pad_perc_w = box_pad_perc_w
        self.verbose = verbose

        super().__init__(*args, **kwargs)

        self.load_image()

    def run(self):
        pyglet.app.run()

    def rect_rel_to_image(self, rect: Rectangle) -> Rectangle:
        position_x, position_y = self.gl_sprite.position
        return (rect.copy()
                .normalize()
                .shift(-position_x, -position_y)
                .from_top(self.height)
                .scale(1 / self.gl_sprite.scale))

    def rect_rel_to_window(self, rect: Rectangle) -> Rectangle:
        position_x, position_y = self.gl_sprite.position
        return (rect.copy()
                .scale(self.gl_sprite.scale)
                .from_bottom(self.height)
                .shift(position_x, position_y))

    def rect_to_box(self,
                    rect: Rectangle,
                    ratio: float,
                    pad_perc_w: float=0.2) -> Rectangle:
        normalized = rect.copy().normalize()
        sprite_rect = Rectangle(
            self.gl_sprite.position[0],
            self.gl_sprite.position[1],
            self.gl_sprite.width,
            self.gl_sprite.height
        )
        return (normalized
                .create_box(ratio)
                .pad_by_perc_w(pad_perc_w)
                .limit(sprite_rect.w, sprite_rect.h)
                .center(normalized)
                .move_inside(sprite_rect))

    def load_background(self):
        self.gl_image = pyglet.image.load(self.current_image)
        self.gl_sprite = pyglet.sprite.Sprite(img=self.gl_image)
        if self.verbose:
            msg = 'loaded {idx}/{length}: {path}'.format(
                idx=self.cursor + 1,
                length=len(self.images),
                path=self.current_image
            )
            print(msg, file=sys.stderr)

    def load_objects(self):
        selection = Selection(box_ratio=self.box_ratio,
                              box_pad_perc_w=self.box_pad_perc_w)
        if self.current_mark.rect:
            selection.from_px(self.current_mark.rect, self)
        self.objects = [selection]

    def load_image(self, incr: int=0):
        self.cursor += incr
        if self.cursor >= len(self.images):
            self.cursor = 0
        self.current_image = self.images[self.cursor]
        self.current_mark = self.marks.get(self.current_image, Mark())

        self.load_background()
        self.scale()
        self.load_objects()

    def save_image(self):
        selection = self.objects[0]
        if selection and selection.w and selection.h:
            self.current_mark.rect = selection.to_px(self)
            self.current_mark.box = selection.to_box_px(self)
        self.marks[self.current_image] = self.current_mark
        self.callback(self.current_image, self.current_mark)

    def scale(self):
        ratio, position_x, position_y = fit(
            self.gl_image.width,
            self.gl_image.height,
            self.width,
            self.height
        )
        self.gl_sprite.scale = ratio
        self.gl_sprite.position = (position_x, position_y)

    def draw_background(self):
        self.gl_sprite.draw()

    def draw_text(self):
        if not self.current_mark.note:
            return
        gl.draw_text(self.current_mark.note, x=20, y=20)

    def on_draw(self):
        self.clear()
        self.scale()
        self.draw_background()
        self.draw_text()
        for obj in self.objects:
            obj.draw(self)

    def on_mouse_press(self, *args, **kwargs):
        for obj in self.objects:
            obj.on_mouse_press(*args, **kwargs)

    def on_mouse_drag(self, *args, **kwargs):
        for obj in self.objects:
            obj.on_mouse_drag(*args, **kwargs)

    def on_key_press(self, symbol, modifiers):
        if symbol in (key.ENTER, key.RIGHT, key.DOWN):
            self.save_image()
            self.load_image(1)
        elif symbol in (key.LEFT, key.UP):
            self.save_image()
            self.load_image(-1)
        elif symbol in (key.ESCAPE, key.Q):
            self.save_image()
            self.close()
        elif symbol == key.BACKSPACE:
            self.current_mark.note = self.current_mark.note[:-1]

    def on_text(self, text):
        if text >= ' ':
            self.current_mark.note += text

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.scale()
        self.load_objects()
