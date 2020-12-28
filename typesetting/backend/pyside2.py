from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QPainter
from PySide2.QtGui import QPdfWriter
from PySide2.QtGui import QFontDatabase, QFontMetricsF
# from PySide2.QtGui import QPen, QPagedPaintDevice
# from PySide2.QtGui import QPageSize
from PySide2.QtGui import QPageLayout
from PySide2.QtCore import QMarginsF, QSizeF
from PySide2.QtCore import Qt
from PySide2.QtCore import QRectF
from PySide2.QtCore import QPoint
from PySide2.QtGui import QPen, QColor, QBrush
from PySide2.QtGui import QImage


from ..units import as_mm, as_inch, mm, inch, as_pt, _quantity
from .._prim import _draw, Graphic, DrawingPrimitive


app = QApplication(['pyside2-backend'])
font_db = QFontDatabase()


def peek_image(path):
    im = QImage(path)
    return im.width(), im.height()


class Font:
    def __init__(self, qt_font, metrics, resolution):
        self.qt_font = qt_font
        self.metrics = metrics
        self.ascent = metrics.ascent() * inch / resolution
        self.descent = metrics.descent() * inch / resolution
        self.height = metrics.height() * inch / resolution
        self.leading = metrics.lineSpacing() * inch / resolution - self.height
        self._resolution = resolution

    def width_of(self, text):
        return self.metrics.width(text) * inch / self._resolution


class TypeFace:
    def __init__(self, name, renderer):
        self.name = name
        self.renderer = renderer

    def __call__(self, point_size):
        qt_font = font_db.font(self.name, "Roman", point_size)
        return Font(
            qt_font,
            QFontMetricsF(qt_font, self.renderer.writer),
            self.renderer.writer.resolution(),
        )


class Pen:
    def __init__(self, qt_pen, qt_brush):
        self.qt_pen = qt_pen
        self.qt_brush = qt_brush

    def ellipse(self, width, height):
        _quantity(width, 'width')
        _quantity(height, 'height')
        return Graphic(
            width, height, 0 * mm, 0 * mm, DrawingPrimitive.ELLIPSE, (self, ))

    def line_to(self, end_x, end_y):
        _quantity(end_x, 'end_x')
        _quantity(end_y, 'end_y')

        return Graphic(
            end_x, end_y, 0 * mm, 0 * mm,
            DrawingPrimitive.LINE, (end_x, end_y, self))

    def polyline(self, *points):
        points = tuple(points)
        width = 0 * mm
        height = 0 * mm

        for p in points:
            x, y = p
            _quantity(x, 'x-positions')
            _quantity(y, 'y-positions')
            if x > width:
                width = x
            if y > height:
                height = y
        return Graphic(
            width, height, 0 * mm, 0 * mm,
            DrawingPrimitive.POLYLINE, (self, *points))

    def rectangle(self, width, height):
        _quantity(width, 'width')
        _quantity(height, 'height')
        return Graphic(
            width, height, 0 * mm, 0 * mm,
            DrawingPrimitive.RECTANGLE, (self, ))


class Renderer:
    def __init__(self, path):
        self.painter = None
        self.writer = QPdfWriter(path)
        margins = QMarginsF(0, 0, 0, 0)
        self.writer.setPageMargins(margins, QPageLayout.Millimeter)

    def type_face(self, name):
        return TypeFace(name, self)

    def draw_ellipse(self, x, y, width, height, pen):
        self.painter.setPen(pen.qt_pen)
        self.painter.setBrush(pen.qt_brush)
        self.painter.drawEllipse(
            self.pts(x), self.pts(y), self.pts(width), self.pts(height))

    def draw_image(self, x, y, width, height, path, crop=None):
        image = QImage(path)
        rect = QRectF(self.pts(x), self.pts(y), self.pts(width), self.pts(height))
        if crop is None:
            self.painter.drawImage(rect, image)
        else:
            sx, sy, sw, sh = crop
            source_rect = QRectF(
                sx * image.width(),
                sy * image.height(),
                sw * image.width(),
                sh * image.height(),
            )
            self.painter.drawImage(rect, image, source_rect)

    def draw_polyline(self, pen, *points):
        self.painter.setPen(pen.qt_pen)
        self.painter.setBrush(pen.qt_brush)
        self.painter.drawPolyline(
            [QPoint(self.pts(x), self.pts(y)) for x, y in points])

    def draw_line(self, start, end, pen):
        self.painter.setPen(pen.qt_pen)
        self.painter.drawLine(
            self.pts(start[0]), self.pts(start[1]), self.pts(end[0]), self.pts(end[1]))

    def draw_rectangle(self, x, y, width, height, pen):
        self.painter.setPen(pen.qt_pen)
        self.painter.setBrush(pen.qt_brush)
        self.painter.drawRect(
            self.pts(x), self.pts(y), self.pts(width), self.pts(height))

    def draw_text(self, x, y, font, string, indent=0 * mm):
        self.painter.setFont(font.qt_font)
        self.painter.setPen(Qt.black)
        self.painter.drawText(self.pts(x + indent), self.pts(y + font.ascent), string)

    def new_page(self, width, height):
        size = QSizeF(as_mm(width), as_mm(height))
        self.writer.setPageSizeMM(size)
        if self.painter is None:
            self.painter = QPainter(self.writer)
        else:
            self.writer.newPage()

    def pen(self, width, color=(0, 0, 0), fill_color=None, round_cap=True, round_join=False):
        if fill_color is None:
            qt_brush = Qt.NoBrush
        else:
            qt_brush = QBrush(QColor(*fill_color))

        if color is None:
            qt_pen = Qt.NoPen
        else:
            qt_pen = QPen(
                QBrush(QColor(*color)),
                as_pt(width),
                cap=Qt.RoundCap if round_cap else Qt.FlatCap,
                join=Qt.RoundJoin if round_join else Qt.BevelJoin,
            )

        return Pen(qt_pen, qt_brush)

    def pts(self, distance):
        return as_inch(distance) * self.writer.resolution()

    def render(self, *pages, debug):
        for page in pages:
            if debug:
                print("Traversing page:")
            self.new_page(page.width, page.height)
            _draw(self, page, (0 * mm, 0 * mm), debug_indent=0 if debug else None)

        self.save()

    def save(self):
        self.painter.end()
        self.painter = None
