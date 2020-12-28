import functools

from . import textual
from .backend import get_backend
from .units import mm, inch, _quantity
from ._prim import Frame, Graphic, LazyPage, DrawingPrimitive


def center(node, width=None, height=None):
    if width is None:
        width = node.width
    if height is None:
        height = node.height
    x = (width - node.width) / 2
    y = (height - node.height) / 2
    return Frame(
        width, height, 0 * mm, 0 * mm, (node.at(x, y), ), 'centered')


def centered(width=None, height=None):
    _quantity(width, 'width')
    _quantity(height, 'height')

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            center(func(*args, **kwargs), width, height)

        return wrapper
    return decorator


def frame(*nodes, name='group', width=None, height=None):
    if width is None:
        w = max(n.x + n.width for n in nodes)
    else:
        w = width
    if height is None:
        h = max(n.y + n.height for n in nodes)
    else:
        h = height
    return Frame(w, h, 0 * mm, 0 * mm, nodes, name)


def framed(width=None, height=None):
    _quantity(width, 'width', or_none=True)
    _quantity(height, 'height', or_none=True)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return frame(
                *func(*args, **kwargs),
                width=width,
                height=height,
                name=func.__name__,
            )

        return wrapper
    return decorator


def image(path, width=None, height=None):
    _quantity(width, 'width', or_none=True)
    _quantity(height, 'height', or_none=True)

    if width is None or height is None:
        dimensions = get_backend().peek_image(path)
        if width is None and height is None:
            width = dimensions[0] / 300 * inch
            height = dimensions[1] / 300 * inch
        elif height is None:
            height = width * dimensions[1] / dimensions[0]
        elif width is None:
            width = height * dimensions[0] / dimensions[1]
    return Graphic(
        width, height, 0 * mm, 0 * mm, DrawingPrimitive.IMAGE, (path, ))


def padding(width, height):
    _quantity(width, 'width')
    _quantity(height, 'height')
    return Frame(width, height, 0 * mm, 0 * mm, (), 'padding')


def page(page_size, *margins):
    size_tuple = LazyPage.size(page_size)
    margin_tuple = LazyPage.margins(*margins)
    content_width = size_tuple[0] - margin_tuple[1] - margin_tuple[3]
    content_height = size_tuple[1] - margin_tuple[0] - margin_tuple[2]

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            generator = func(content_width, content_height, *args, **kwargs)
            return LazyPage(size_tuple, margin_tuple, generator, func.__name__)

        return wrapper
    return decorator


def paragraph(font, string, width):
    _quantity(width, 'width')
    y = 0 * mm
    children = []
    for line in textual.naive_wrap(font, string, width):
        children.append(text_frame(font, ' '.join(line)).at(0 * mm, y))
        y += font.height
    return Frame(width, y, 0 * mm, 0 * mm, tuple(children), 'paragraph')


def renderer(*args, **kwargs):
    return get_backend().Renderer(*args, **kwargs)


@framed()
def stack(*drawables):
    y = 0 * mm
    for c in drawables:
        yield c.at(x=c.x, y=y)
        y += c.height


def text_frame(font, string, *, center_of=None, shrink_to_ascent=False):
    _quantity(center_of, 'center_of', or_none=True)
    width = font.width_of(string)

    if shrink_to_ascent:
        height = font.ascent
    else:
        height = font.height

    if center_of is None:
        x = 0 * mm
    else:
        x = (center_of - width) / 2
        width = center_of

    return Graphic(
        width, height, 0 * mm, 0 * mm,
        DrawingPrimitive.TEXT, (font, string, x))
