import collections
import enum
import functools

from .backend import get_backend
from .units import mm


class Frame(
        collections.namedtuple("_Frame", "width height x y children")):
    __slots__ = ()

    def at(self, x, y):
        return self._replace(x=x, y=y)


class Graphic(
        collections.namedtuple("_Graphic", "width height x y draw args")):
    __slots__ = ()

    def at(self, x, y):
        return self._replace(x=x, y=y)


class DrawingPrimitive(enum.Enum):
    RECTANGLE = 4
    TEXT = 10


def centered(width, height):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            contents = func(*args, **kwargs)
            x = (width - contents.width) / 2
            y = (height - contents.height) / 2
            return Frame(width, height, 0, 0, (contents.at(x, y), ))

        return wrapper
    return decorator


def _draw(rdr, node, pos):
    x, y = pos
    if isinstance(node, Frame):
        for child in node.children:
            _draw(rdr, child, (x + child.x, y + child.y))

    elif isinstance(node, Graphic):
        if isinstance(node.draw, DrawingPrimitive):
            if node.draw == DrawingPrimitive.RECTANGLE:
                rdr.draw_rectangle(x, y, node.width, node.height)
            elif node.draw == DrawingPrimitive.TEXT:
                rdr.draw_text(x, y, *node.args)
            else:
                assert 0, node.draw

        else:
            assert 0, repr(node.draw)


def framed(width, height):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            children = tuple(func(*args, **kwargs))
            return Frame(width, height, 0 * mm, 0 * mm, children)

        return wrapper
    return decorator


def prepare(path, type_faces=()):
    backend = get_backend()
    rdr = backend.Renderer(path)

    for face in type_faces:
        face.bind(rdr)

    def render(*pages):
        for page in pages:
            rdr.new_page(page.width, page.height)
            _draw(rdr, page, (0 * mm, 0 * mm))

        rdr.save()

    return render


def rectangle(width, height):
    return Graphic(
        width, height, 0 * mm, 0 * mm, DrawingPrimitive.RECTANGLE, None)


def text_frame(font, string, *, center_of=None, shrink_to_ascent=False):
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
        DrawingPrimitive.TEXT, (font, "Summary", x))
