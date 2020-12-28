import functools

from . import textual
from .backend import get_backend
from .units import mm, inch, _quantity
from ._prim import Frame, Graphic, LazyPage, DrawingPrimitive, _draw


def centered(width, height):
    _quantity(width, 'width')
    _quantity(height, 'height')

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            contents = func(*args, **kwargs)
            x = (width - contents.width) / 2
            y = (height - contents.height) / 2
            return Frame(
                width, height, 0 * mm, 0 * mm, (contents.at(x, y), ), 'centered')

        return wrapper
    return decorator


def ellipse(width, height, fill=None):
    _quantity(width, 'width')
    _quantity(height, 'height')
    return Graphic(
        width, height, 0 * mm, 0 * mm, DrawingPrimitive.ELLIPSE, (fill, ))


def framed(width=None, height=None):
    _quantity(width, 'width', or_none=True)
    _quantity(height, 'height', or_none=True)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            children = tuple(func(*args, **kwargs))
            if width is None:
                w = max(c.x + c.width for c in children)
            else:
                w = width
            if height is None:
                h = max(c.y + c.height for c in children)
            else:
                h = height
            return Frame(w, h, 0 * mm, 0 * mm, children, func.__name__)

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


def line_to(end_x, end_y):
    _quantity(end_x, 'end_x')
    _quantity(end_y, 'end_y')

    return Graphic(
        end_x, end_y, 0 * mm, 0 * mm, DrawingPrimitive.LINE, (end_x, end_y))


def padding(width, height):
    _quantity(width, 'width')
    _quantity(height, 'height')
    return Frame(width, height, 0 * mm, 0 * mm, (), 'padding')


def page(page_size, *margins):
    size_tuple = LazyPage.size(page_size)
    margin_tuple = LazyPage.margins(*margins)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            generator = func(*args, **kwargs)
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


def rectangle(width, height):
    _quantity(width, 'width')
    _quantity(height, 'height')
    return Graphic(
        width, height, 0 * mm, 0 * mm, DrawingPrimitive.RECTANGLE, None)


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