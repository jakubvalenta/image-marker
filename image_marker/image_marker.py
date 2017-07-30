#!/usr/bin/env python

import os
import sys

import click
import pyglet
from pyglet.window import key, mouse


COLOR_RED = (255, 0, 0, 255)


class ImageMarker(pyglet.window.Window):
    paths = None
    callback = None
    screen_width = None
    screen_height = None
    idx = 0
    selection = None

    def __init__(self, paths, callback, *args, **kwargs):
        self.paths = paths
        self.callback = callback
        super().__init__(*args, **kwargs)
        self.screen_width = self.width
        self.screen_height = self.height
        self.load_image()

    def load_image(self, incr=0):
        length = len(self.paths)
        self.idx += incr
        if self.idx >= length:
            self.idx = 0
        path = self.paths[self.idx]
        self.image = pyglet.resource.image(path)
        self.sprite = pyglet.sprite.Sprite(img=self.image)
        print('loaded {}/{}: {}'.format(self.idx + 1, length, path),
              file=sys.stderr)

    @property
    def path(self):
        return self.paths[self.idx]

    @property
    def selection_px(self):
        rect = self.selection
        vertex_1 = rect[:2]
        vertex_2 = rect[0] + rect[2], rect[1] + rect[3]
        left = min(vertex_1[0], vertex_2[0])
        top = max(vertex_1[1], vertex_2[1])
        width = abs(rect[2])
        height = abs(rect[3])
        return [round(x / self.sprite.scale) for x in (
            left - self.sprite.position[0],
            self.screen_height - top - self.sprite.position[1],
            width,
            height,
        )]

    def reset_selection(self, x=0, y=0):
        self.selection = [x, y, 0, 0]

    @staticmethod
    def draw_rect(x, y, w, h, color=COLOR_RED):
        vertex_list = pyglet.graphics.vertex_list(
            4,
            ('v2f', (x, y, x, y + h, x + w, y + h, x + w, y)),
            ('c4B', color * 4)
        )
        vertex_list.draw(pyglet.gl.GL_LINE_LOOP)

    @staticmethod
    def fit(image_w, image_h, container_w, container_h):
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
            self.image.width,
            self.image.height,
            self.screen_width,
            self.screen_height
        )
        self.sprite.scale = ratio
        self.sprite.position = (position_x, position_y)
        self.sprite.draw()
        if self.selection:
            self.draw_rect(*self.selection)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.reset_selection(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT:
            self.selection[2] += dx
            self.selection[3] += dy

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.callback(self.path, self.selection_px)

    def on_key_press(self, symbol, modifiers):
        if symbol in (key.ENTER, key.SPACE, key.RIGHT, key.DOWN):
            self.reset_selection()
            self.load_image(1)
        elif symbol in (key.LEFT, key.UP):
            self.reset_selection()
            self.load_image(-1)
        elif symbol in (key.ESCAPE, key.Q):
            self.close()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.screen_width, self.screen_height = width, height


@click.command()
@click.argument('images_dir')
def cli(images_dir):
    paths = [os.path.join(images_dir, x)
             for x in sorted(os.listdir(images_dir))]

    def callback(path, selection):
        print(path, *selection)

    ImageMarker(paths, callback, resizable=True)
    pyglet.app.run()


if __name__ == '__main__':
    cli()
