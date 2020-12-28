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
from PySide2.QtGui import QPen, QColor, QBrush
from PySide2.QtGui import QImage


from ..units import as_mm, as_inch, mm, inch
from .._prim import _draw


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


class Renderer:
    def __init__(self, path):
        self.painter = None
        self.writer = QPdfWriter(path)
        margins = QMarginsF(0, 0, 0, 0)
        self.writer.setPageMargins(margins, QPageLayout.Millimeter)

    def type_face(self, name):
        return TypeFace(name, self)

    def draw_ellipse(self, x, y, width, height, border_width=8, color=Qt.black, fill=None):
        if fill is not None:
            b = self.painter.brush()
            self.painter.setBrush(QBrush(QColor(*fill)))
        else:
            b = None
        self.painter.setPen(QPen(
            color, border_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.painter.drawEllipse(
            self.pts(x), self.pts(y), self.pts(width), self.pts(height))
        if b:
            self.painter.setBrush(b)

    def draw_image(self, path, x, y, width, height):
        image = QImage(path)
        rect = QRectF(self.pts(x), self.pts(y), self.pts(width), self.pts(height))
        self.painter.drawImage(rect, image)

    def draw_line(self, start, end, border_width=8, color=Qt.black):
        self.painter.setPen(QPen(
            color, border_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.painter.drawLine(
            self.pts(start[0]), self.pts(start[1]), self.pts(end[0]), self.pts(end[1]))

    def draw_rectangle(self, x, y, width, height, border_width=8, color=Qt.black, fill=None):
        if fill is not None:
            b = self.painter.brush()
            self.painter.setBrush(QBrush(QColor(*fill)))
        else:
            b = None
        self.painter.setPen(QPen(
            color, border_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.painter.drawRect(
            self.pts(x), self.pts(y), self.pts(width), self.pts(height))
        if b:
            self.painter.setBrush(b)

    def draw_text(self, x, y, font, string, indent=0 * mm):
        self.painter.setFont(font.qt_font)
        self.painter.drawText(self.pts(x + indent), self.pts(y + font.ascent), string)

    def new_page(self, width, height):
        size = QSizeF(as_mm(width), as_mm(height))
        self.writer.setPageSizeMM(size)
        if self.painter is None:
            self.painter = QPainter(self.writer)
        else:
            self.writer.newPage()

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
