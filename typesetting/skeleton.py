"""How we represent a document as it is laid out."""

from collections import namedtuple

from .units import as_pt

Font = namedtuple('Font', 'ascent descent height leading')

Page = namedtuple('Page', 'xwidth xheight')
Column = namedtuple('Column', 'page id x y width height')
Line = namedtuple('Line', 'previous column y graphics')

def single_column_layout(width, height, top, bottom, inner, outer):
    column_width = width - inner - outer
    column_height = height - top - bottom

    def new_page():
        return Page(width, height)

    def next_column(column):
        page = new_page()
        id = column.id + 1 if column else 1
        if id % 2:
            left = inner
        else:
            left = outer
        return Column(page, id, as_pt(left), as_pt(top), as_pt(column_width), as_pt(column_height))

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


def frame_layout(frames, page_width, page_height):
    def new_page():
        return Page(page_width, page_height)

    def next_column(column):
        if column:
            new_id = column.id + 1
            page = column.page if new_id < len(frames) else new_page()
        else:
            new_id = 0
            page = new_page()
        new_id %= len(frames)
        return Column(page, new_id, *frames[new_id])

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

# def new_page():
#     return Page(10, 34)

# def next_column(column):
#     page = new_page()
#     id = column.id + 1 if column else 1
#     return Column(page, id, 0, 0, 10, 34)

# def next_line(line, leading, height):
#     if line:
#         column = line.column
#         y = line.y + height + leading
#         if y <= column.height:
#             return Line(line, column, y, [])
#     else:
#         column = None
#     return Line(line, next_column(column), height, [])

def unroll(start_line, end_line):
    lines = [end_line]
    while end_line is not start_line:
        end_line = end_line.previous
        lines.append(end_line)
    lines.reverse()
    return lines
