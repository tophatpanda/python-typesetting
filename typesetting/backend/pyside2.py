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


from ..units import as_mm, as_inch, mm, pt, inch


app = QApplication(['pyside2-backend'])
font_db = QFontDatabase()


def peek_image(path):
    im = QImage(path)
    return im.width(), im.height()


class Font:
    def __init__(self, qt_font, metrics):
        self.qt_font = qt_font
        self.metrics = metrics
        self.ascent = metrics.ascent() * inch / 1200
        self.descent = metrics.descent() * inch / 1200
        self.height = metrics.height() * inch / 1200
        self.leading = metrics.lineSpacing() * inch / 1200 - self.height

    def width_of(self, text):
        return self.metrics.width(text) * inch / 1200


class TypeFace:
    def __init__(self, name):
        self.name = name
        self._writer = None

    def bind(self, renderer):
        self._writer = renderer.writer

    def __call__(self, point_size, renderer=None):
        if renderer is None:
            if self._writer is None:
                raise RuntimeError("Can't produce font without a renderer")
            else:
                writer = self._writer
        else:
            writer = renderer.writer

        qt_font = font_db.font(self.name, "Roman", point_size)
        return Font(qt_font, QFontMetricsF(qt_font, writer))


class Renderer:
    def __init__(self, path):
        self.painter = None
        self.writer = QPdfWriter(path)
        margins = QMarginsF(0, 0, 0, 0)
        self.writer.setPageMargins(margins, QPageLayout.Millimeter)

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

    def save(self):
        self.painter.end()
        self.painter = None
