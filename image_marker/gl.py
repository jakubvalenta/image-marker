from typing import Tuple

import pyglet

from image_marker.rect import Rectangle


TColor = Tuple[int, int, int, int]

COLOR_RED = (255, 0, 0, 255)
COLOR_GREEN = (0, 255, 0, 255)
COLOR_BLUE = (0, 0, 255, 255)


def draw_rect(rect: Rectangle, color: TColor=COLOR_RED):
    x, y, w, h = rect.x, rect.y, rect.w, rect.h
    vertex_list = pyglet.graphics.vertex_list(
        4,
        ('v2f', (x, y, x, y + h, x + w, y + h, x + w, y)),
        ('c4B', color * 4)
    )
    vertex_list.draw(pyglet.gl.GL_LINE_LOOP)


def draw_text(s: str,
              font_name: str='sans-serif',
              font_size: int=24,
              color: TColor=COLOR_BLUE,
              **kwargs):
    label = pyglet.text.Label(
        s,
        color=color,
        font_name=font_name,
        font_size=font_size,
        **kwargs
    )
    label.draw()
