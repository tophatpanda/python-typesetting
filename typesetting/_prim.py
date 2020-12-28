import collections
import enum
from .units import mm, as_mm, _quantity


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
                rdr.draw_rectangle(x, y, node.width, node.height, *node.args)
            elif node.draw == DrawingPrimitive.LINE:
                dx, dy, pen = node.args
                rdr.draw_line((x, y), (x + dx, y + dy), pen)
            elif node.draw == DrawingPrimitive.ELLIPSE:
                rdr.draw_ellipse(x, y, node.width, node.height, *node.args)
            elif node.draw == DrawingPrimitive.TEXT:
                rdr.draw_text(x, y, *node.args)
            elif node.draw == DrawingPrimitive.IMAGE:
                path, = node.args
                rdr.draw_image(path, x, y, node.width, node.height)
            else:
                assert 0, node.draw

        else:
            assert 0, repr(node.draw)
    else:
        raise TypeError(f"{node!r} is not drawable")
