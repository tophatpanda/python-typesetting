import collections
import enum
import functools

from . import textual
from .backend import get_backend
from .units import mm, inch, as_mm, _quantity


def _rough(quantity):
    try:
        return round(as_mm(quantity), 1)
    except AttributeError:
        return "ERR"


class Node:
    __slots__ = ()

    def at(self, x, y):
        _quantity(x, 'y')
        _quantity(x, 'y')
        return self._replace(x=x, y=y)

    def move(self, dx, dy):
        return self.at(self.x + dx, self.y + dy)

    def __str__(self):
        return "{t} ({n}) {w}×{h} @ {x},{y} [mm]".format(
            t=self.__class__.__qualname__,
            n=self.name,
            w=_rough(self.width),
            h=_rough(self.height),
            x=_rough(self.x),
            y=_rough(self.y),
        )


# These names are overwritten by the proper class
Frame = collections.namedtuple("_Frame", "width height x y children name")
Graphic = collections.namedtuple("_Graphic", "width height x y draw args")


class Frame(Frame, Node):
    __slots__ = ()


class Graphic(Graphic, Node):
    __slots__ = ()

    @property
    def name(self):
        if isinstance(self.draw, DrawingPrimitive):
            return self.draw.name
        else:
            return self.draw.__name__


class LazyPage(Node):
    @staticmethod
    def margins(top, right=None, bottom=None, left=None):
        if right is None:
            right = top
        if bottom is None:
            bottom = top
        if left is None:
            left = right
        return top, right, bottom, left

    @staticmethod
    def size(source):
        if isinstance(source, str):
            sizes = {
                'A0': (841 * mm, 1189 * mm),
                'A1': (594 * mm, 841 * mm),
                'A2': (420 * mm, 594 * mm),
                'A3': (297 * mm, 420 * mm),
                'A4': (210 * mm, 297 * mm),
                'A5': (148 * mm, 210 * mm),
                'A6': (105 * mm, 148 * mm),
                'A7': (74 * mm, 105 * mm),
                'A8': (52 * mm, 74 * mm),
                'A9': (37 * mm, 52 * mm),
                'B0': (1000 * mm, 1414 * mm),
                'B1': (707 * mm, 1000 * mm),
                'B2': (500 * mm, 707 * mm),
                'B3': (353 * mm, 500 * mm),
                'B4': (250 * mm, 353 * mm),
                'B5': (176 * mm, 250 * mm),
                'B6': (125 * mm, 176 * mm),
                'B7': (88 * mm, 125 * mm),
                'B8': (62 * mm, 88 * mm),
                'B9': (44 * mm, 62 * mm),
                'B10': (31 * mm, 44 * mm),
                'C5E': (163 * mm, 229 * mm),
                'Comm10E': (105 * mm, 241 * mm),
                'DLE': (110 * mm, 220 * mm),
                'Executive': (190.5 * mm, 254 * mm),
                'Folio': (210 * mm, 330 * mm),
                'Ledger': (431.8 * mm, 279.4 * mm),
                'Legal': (215.9 * mm, 355.6 * mm),
                'Letter': (215.9 * mm, 279.4 * mm),
                'Tabloid': (279.4 * mm, 431.8 * mm),
                }
            return sizes[source]
        else:
            # conform to be a two-tuple
            width, height = source
            return (width, height)

    def __init__(self, size_tuple, margin_tuple, children, name):
        self.width, self.height = size_tuple
        _quantity(self.width, 'width')
        _quantity(self.height, 'height')

        top, right, bottom, left = margin_tuple
        _quantity(top, 'top margin')
        _quantity(right, 'right margin')
        _quantity(bottom, 'bottom margin')
        _quantity(left, 'left margin')
        self.content_width = self.width - left - right
        self.content_height = self.height - top - bottom

        self.x = 0 * mm
        self.y = 0 * mm
        self.content_x = left
        self.content_y = top

        self.children = (
            c.move(self.content_x, self.content_y) for c in children)
        self.name = name

    def __str__(self):
        return "{t} ({d}) {w}×{h} @ {x},{y} [mm]".format(
            t=self.__class__.__qualname__,
            d=self.name,
            w=round(as_mm(self.width), 1),
            h=round(as_mm(self.height), 1),
            x=round(as_mm(self.x), 1),
            y=round(as_mm(self.y), 1),
        )


class DrawingPrimitive(enum.Enum):
    ELLIPSE = 0
    LINE = 2
    RECTANGLE = 4
    TEXT = 10
    IMAGE = 11


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


def _draw(rdr, node, pos, debug_indent):
    if debug_indent is not None:
        print(" " * debug_indent, "└", node)

    if isinstance(node, Frame) or isinstance(node, LazyPage):
        x, y = pos
        for child in node.children:
            if debug_indent is None:
                _indent = None
            else:
                _indent = debug_indent + 1
            _draw(rdr, child, (x + node.x, y + node.y), _indent)

    elif isinstance(node, Graphic):
        x, y = pos
        x += node.x
        y += node.y
        if isinstance(node.draw, DrawingPrimitive):
            if node.draw == DrawingPrimitive.RECTANGLE:
                rdr.draw_rectangle(x, y, node.width, node.height)
            elif node.draw == DrawingPrimitive.TEXT:
                rdr.draw_text(x, y, *node.args)
            elif node.draw == DrawingPrimitive.ELLIPSE:
                fill, = node.args
                rdr.draw_ellipse(x, y, node.width, node.height, fill=fill)
            elif node.draw == DrawingPrimitive.LINE:
                dx, dy = node.args
                rdr.draw_line((x, y), (x + dx, y + dy))
            elif node.draw == DrawingPrimitive.IMAGE:
                path, = node.args
                rdr.draw_image(path, x, y, node.width, node.height)
            else:
                assert 0, node.draw

        else:
            assert 0, repr(node.draw)
    else:
        raise TypeError(f"{node!r} is not drawable")


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


def prepare(path, type_faces=()):
    backend = get_backend()
    rdr = backend.Renderer(path)

    for face in type_faces:
        face.bind(rdr)

    def render(*pages, debug=False):
        for page in pages:
            print("Traversing page:")
            rdr.new_page(page.width, page.height)
            _draw(rdr, page, (0 * mm, 0 * mm), debug_indent=0 if debug else None)

        rdr.save()

    return render


def rectangle(width, height):
    _quantity(width, 'width')
    _quantity(height, 'height')
    return Graphic(
        width, height, 0 * mm, 0 * mm, DrawingPrimitive.RECTANGLE, None)


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
