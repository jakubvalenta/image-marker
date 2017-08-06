from typing import Tuple


def fit(image_w: int,
        image_h: int,
        container_w: int,
        container_h: int) -> Tuple[float, int, int]:
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


def contain(w: int, h: int, container_ratio: float):
    ratio = w / h
    if ratio > container_ratio:
        container_w = w
        container_h = w / container_ratio
    else:
        container_h = h
        container_w = h * container_ratio
    return container_w, container_h
