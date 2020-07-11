#!/usr/bin/env python

import csv
import os
import sys
from typing import IO, Iterator, Union

import click

from image_marker.app import App, Mark, Rectangle, TMarks, TPath


def read_paths(dir_path: TPath) -> Iterator[TPath]:
    with os.scandir(dir_path) as it:
        for entry in it:
            if entry.is_file():
                yield os.path.join(dir_path, entry.name)


def read_marks(path: TPath) -> TMarks:
    out: TMarks = {}
    if path:
        if not os.path.isfile(path):
            print('Input marks file doesn\'t exist.')
            return out
        with open(path) as f:
            reader = csv.reader(f, delimiter=' ')
            for line in reader:
                path, x, y, w, h, note = line
                rect = Rectangle.from_strings(x, y, w, h)
                out[path] = Mark(rect=rect, note=note)
    return out


def write_marks(marks: TMarks, path_or_file: Union[IO, TPath], rect_prop: str):
    if isinstance(path_or_file, str):
        f: IO = open(path_or_file, 'w')
    else:
        f = path_or_file
    writer = csv.writer(f, delimiter=' ')
    for path, mark in marks.items():
        rect = getattr(mark, rect_prop)
        if rect:
            writer.writerow([path] + list(rect.to_strings()) + [mark.note])
    if isinstance(path_or_file, str):
        f.close()


@click.command()
@click.argument('images_dir')
@click.option(
    '--marks',
    '-m',
    'marks_path',
    help='Marks CSV file path. It will be used to load existing '
    'marks as well as to write new marks. Defaults to "-", which '
    'means stdout.',
    default='-',
)
@click.option(
    '--output',
    '-o',
    'output_path',
    help='Output CSV file path. It will contain the boxes if '
    '--box-ratio is passed, otherwise it will be the same as '
    '--marks. Defaults to "-", which means stdout.',
    default='-',
)
@click.option('--box-ratio', '-br', type=float, default=0)
@click.option('--box-pad-perc-w', '-bp', type=float, default=0)
@click.option('--verbose', '-v', is_flag=True)
def cli(
    images_dir: str,
    marks_path: str,
    output_path: str,
    box_ratio: float,
    box_pad_perc_w: float,
    verbose: bool,
):
    paths = list(sorted(read_paths(images_dir)))
    marks = read_marks(marks_path)
    out = {}

    def callback(path: str, mark: Mark):
        out.update({path: mark})
        if marks_path:
            write_marks(out, marks_path, 'rect')
        if output_path == '-':
            write_marks({path: mark}, sys.stdout, 'box')
        else:
            write_marks(out, output_path, 'box')
        if verbose:
            write_marks({path: mark}, sys.stderr, 'box')

    app = App(
        paths,
        marks,
        callback,
        box_ratio,
        box_pad_perc_w,
        verbose,
        resizable=True,
    )
    app.run()


if __name__ == '__main__':
    cli()
