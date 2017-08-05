#!/usr/bin/env python

import attr
import os
import sys

import click
import pyglet
from pyglet.window import key, mouse

from typing import Callable, Dict, Iterable, Iterator, List, Tuple


@attr.s
class Rectangle():
    x = attr.ib()
    y = attr.ib()
    w = attr.ib()
    h = attr.ib()


TPath = str
TColor = Tuple[int, int, int, int]
TMarks = Dict[TPath, Rectangle]

COLOR_RED = (255, 0, 0, 255)


class ImageMarker(pyglet.window.Window):
    images = None
    marks = None
    callback = None
    current_image_idx = 0
    current_mark = None

    def __init__(self,
                 images: List[TPath],
                 marks: TMarks,
                 callback: Callable[[TPath, Rectangle], None],
                 *args,
                 **kwargs):
        self.images = images
        self.marks = marks
        self.callback = callback
        super().__init__(*args, **kwargs)
        self.load_image()

    @property
    def current_image(self) -> TPath:
        return self.images[self.current_image_idx]

    def rect_to_mark(self, rect: Rectangle) -> Rectangle:
        vertex_1 = rect.x, rect.y
        vertex_2 = rect.x + rect.w, rect.y + rect.h
        left = min(vertex_1[0], vertex_2[0])
        top = max(vertex_1[1], vertex_2[1])
        width = abs(rect.w)
        height = abs(rect.h)
        coord_original = (
            left - self.gl_sprite.position[0],
            self.height - top - self.gl_sprite.position[1],
            width,
            height,
        )
        coord_scaled = map(lambda x: round(x / self.gl_sprite.scale),
                           coord_original)
        return Rectangle(*coord_scaled)

    def mark_to_rect(self, mark: Rectangle) -> Rectangle:
        scale = self.gl_sprite.scale
        position_x, position_y = self.gl_sprite.position
        return Rectangle(
            x=mark.x * scale + position_x,
            y=self.height - position_y - (mark.y + mark.h) * scale,
            w=mark.w * scale,
            h=mark.h * scale
        )

    def reload_rect(self):
        self.gl_rect = None

    def load_image(self, incr: int=0):
        length = len(self.images)
        self.current_image_idx += incr
        if self.current_image_idx >= length:
            self.current_image_idx = 0
        self.current_mark = self.marks.get(self.current_image)
        self.reload_rect()
        self.gl_image = pyglet.resource.image(self.current_image)
        self.gl_sprite = pyglet.sprite.Sprite(img=self.gl_image)
        msg = 'loaded {idx}/{length}: {path}'.format(
            idx=self.current_image_idx + 1,
            length=length,
            path=self.current_image
        )
        print(msg, file=sys.stderr)

    @staticmethod
    def draw_rect(rect: Rectangle, color: TColor=COLOR_RED):
        x, y, w, h = rect.x, rect.y, rect.w, rect.h
        vertex_list = pyglet.graphics.vertex_list(
            4,
            ('v2f', (x, y, x, y + h, x + w, y + h, x + w, y)),
            ('c4B', color * 4)
        )
        vertex_list.draw(pyglet.gl.GL_LINE_LOOP)

    @staticmethod
    def fit(image_w: int,
            image_h: int,
            container_w: int,
            container_h: int) -> Tuple[int, int, int]:
        ratio_w = container_w / image_w
        ratio_h = container_h / image_h
        if ratio_w < ratio_h:
            ratio = ratio_w
            position_x = 0
            position_y = (container_h - image_h * ratio_w) / 2
        else:
            ratio = ratio_h
            position_x = (container_w - image_w * ratio_h) / 2
            position_y = 0
        return ratio, position_x, position_y

    def on_draw(self):
        self.clear()
        ratio, position_x, position_y = self.fit(
            self.gl_image.width,
            self.gl_image.height,
            self.width,
            self.height
        )
        self.gl_sprite.scale = ratio
        self.gl_sprite.position = (position_x, position_y)
        self.gl_sprite.draw()
        if self.gl_rect:
            self.draw_rect(self.gl_rect)
        elif self.current_mark:
            self.gl_rect = self.mark_to_rect(self.current_mark)
            self.draw_rect(self.gl_rect)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.gl_rect = Rectangle(x, y, 0, 0)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT:
            self.gl_rect.w += dx
            self.gl_rect.h += dy

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.current_mark = self.rect_to_mark(self.gl_rect)
            self.marks[self.current_image] = self.current_mark
            self.callback(self.current_image, self.current_mark)

    def on_key_press(self, symbol, modifiers):
        if symbol in (key.ENTER, key.SPACE, key.RIGHT, key.DOWN):
            self.load_image(1)
        elif symbol in (key.LEFT, key.UP):
            self.load_image(-1)
        elif symbol in (key.ESCAPE, key.Q):
            self.close()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.reload_rect()


def read_paths(dir_path: TPath) -> List[TPath]:
    return [os.path.join(dir_path, x)
            for x in sorted(os.listdir(dir_path))]


def read_marks(marks_path: TPath) -> Iterator[TMarks]:
    out = {}
    if marks_path:
        with open(marks_path) as f:
            for line in f:
                path, x, y, w, h = line.strip().split(' ')
                coords_int = map(int, (x, y, w, h))
                out[path] = Rectangle(*coords_int)
    return out


def write_marks(marks: Iterable[TMarks], path: TPath):
    with open(path, 'w') as f:
        for path, mark in marks.items():
            coords_str = map(str, (mark.x, mark.y, mark.w, mark.h))
            line = ' '.join([path, *coords_str])
            f.write(line + '\n')


@click.command()
@click.argument('images_dir')
@click.option('--marks', '-m', 'marks_path')
@click.option('--output', '-o', 'output_path')
def cli(images_dir, output_path, marks_path):
    paths = read_paths(images_dir)
    marks = read_marks(marks_path)

    if output_path:
        out = {}

        def callback(path, mark):
            out[path] = mark
            write_marks(out, output_path)

    else:
        def callback(path, mark):
            print(path, *mark)

    ImageMarker(paths, marks, callback, resizable=True)
    pyglet.app.run()


if __name__ == '__main__':
    cli()
