#!/usr/bin/env python

import csv
import os
import click
import sys

from typing import IO, Iterable, Iterator, List, Union

from image_marker.image_marker import (
    ImageMarker, Mark, Rectangle, TMarks, TPath
)


def read_paths(dir_path: TPath) -> List[TPath]:
    return [os.path.join(dir_path, x)
            for x in sorted(os.listdir(dir_path))]


def read_marks(path: TPath) -> Iterator[TMarks]:
    out = {}
    if path:
        with open(path) as f:
            reader = csv.reader(f, delimiter=' ')
            for line in reader:
                path, x, y, w, h, note = line
                rect = Rectangle.from_strings(x, y, w, h)
                out[path] = Mark(rect=rect, note=note)
    return out


def write_marks(marks: Iterable[TMarks],
                path_or_file: Union[IO, TPath],
                rect_prop: str):
    if isinstance(path_or_file, str):
        f = open(path_or_file, 'w')
    else:
        f = path_or_file
    writer = csv.writer(f, delimiter=' ')
    for path, mark in marks.items():
        rect = getattr(mark, rect_prop)
        writer.writerow([path] + list(rect.to_strings()) + [mark.note])
    if isinstance(path_or_file, str):
        f.close()


@click.command()
@click.argument('images_dir')
@click.option('--output', '-o', 'output_path')
@click.option('--marks', '-m', 'marks_path')
@click.option('--box-ratio', '-br', type=float, default=0)
@click.option('--box-pad-perc-w', '-bp', type=float, default=0.2)
@click.option('--stdout', '-s', is_flag=True)
@click.option('--verbose', '-v', is_flag=True)
def cli(images_dir: str,
        output_path: str,
        marks_path: str,
        box_ratio: float,
        box_pad_perc_w: float,
        stdout: bool,
        verbose: bool):
    paths = read_paths(images_dir)
    marks = read_marks(marks_path)
    if output_path:
        out = {}

    def callback(path, mark):
        if output_path:
            out.update({path: mark})
            write_marks(out, output_path, 'rect')
        if stdout:
            write_marks({path: mark}, sys.stdout, 'box')
        if verbose:
            write_marks({path: mark}, sys.stderr, 'box')

    image_marker = ImageMarker(
        paths,
        marks,
        callback,
        box_ratio,
        box_pad_perc_w,
        verbose,
        resizable=True
    )
    image_marker.run()


if __name__ == '__main__':
    cli()
