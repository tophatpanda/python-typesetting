import os
import argparse

from typesetting import document as doc
from typesetting import composing as c
from typesetting import knuth
from typesetting.pyside2_backend import get_fonts
from typesetting.skeleton import frame_layout, unroll, Page, Column, Line
from PySide2.QtCore import Qt, QPoint
from PySide2.QtGui import QPen
from typesetting import units

this_dir = os.path.dirname(__file__)

mm = 72 / 25.4


def path_of(name):
    return os.path.join(this_dir, name)


def custom_layout(page_width, page_height):
    first_frames = [
        # left, top, width, height
        (25, 25, 90, 145),
        (120, 105, 80, 90),
        (25, 200, 165, 30),
        (30, 235, 40, 25),
        (110, 235, 75, 40),
    ]
    # add unit to all numbers
    first_frames = [
        (l * mm, t * mm, w * mm, h * mm) for (l, t, w, h)
        in first_frames]

    first_page = Page(page_width, page_height)
    second_page = Page(page_width, page_height)

    second_frames = [
        (20 * mm, 25 * mm, 80 * mm, 245 * mm),
        (110 * mm, 25 * mm, 80 * mm, 245 * mm),
    ]

    def next_page(page):
        return Page(page_width, page_height)

    def next_column(column):
        if column is None:
            new_id = 0
            return Column(first_page, new_id, *first_frames[new_id])
        elif column.page is first_page:
            new_id = column.id + 1
            if new_id < len(first_frames):
                return Column(first_page, new_id, *first_frames[new_id])
            else:
                new_id = 0
                return Column(second_page, new_id, *second_frames[new_id])
        else:
            new_id = column.id + 1
            assert new_id < len(second_frames)
            page = second_page
            return Column(page, new_id, *second_frames[new_id])

    def next_line(line, leading, height):
        if line:
            column = line.column
            y = line.y + height + leading
            if y <= column.height:
                return Line(line, column, y, [])
        else:
            column = None

        return Line(line, next_column(column), height, [])

    return next_line


def render():
    story = []

    with open("dagon.txt", "r", encoding="utf8") as f:
        for line in f:
            if line:
                story.append((c.avoid_widows_and_orphans,))
                story.append((
                    knuth.knuth_paragraph, 0, 0, [('roman', line.rstrip())]))

    renderer = doc.Renderer(210 * units.mm, 297 * units.mm)
    fonts = get_fonts(renderer.painter, [
        ('bold', 'Gentium Basic', 'Bold', 8),
        ('roman', 'Gentium Basic', 'Roman', 8),
    ])

    next_line = custom_layout(210 * units.mm, 297 * units.mm)

    def mark_frames(painter, frames):
        pen = QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        for l, t, w, h in frames:
            pt = 1200 / 72.0
            points = [QPoint(x * pt, y * pt) for x, y in
                      [(l, t), (l + w, t), (l + w, t + h), (l, t + h)]]
            for i in range(len(points)):
                painter.drawLine(points[i], points[(i + 1) % len(points)])

    lines = unroll(None, c.run(story, fonts, None, next_line))
    page = None
    # mark_frames(renderer.painter, frames)

    for line in lines:
        if line is None:
            continue
        if page is not None and page is not line.column.page:
            renderer.new_page()
            # mark_frames(renderer.painter, frames)
        page = line.column.page

        for graphic in line.graphics:
            function, *args = graphic
            function(fonts, line, renderer.painter, *args)

    renderer.painter.end()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    # parser.add_argument("path", type=str, default="book.pdf", nargs="?",
    #                     help="The file path to write the pdf to")
    args = parser.parse_args()

    render()
