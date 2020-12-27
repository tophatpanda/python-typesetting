from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QPainter
from PySide2.QtGui import QPdfWriter
from PySide2.QtGui import QFontDatabase, QFontMetricsF
# from PySide2.QtGui import QPen, QPagedPaintDevice
# from PySide2.QtGui import QPageSize
from PySide2.QtGui import QPageLayout
from PySide2.QtCore import QMarginsF, QSizeF
from PySide2.QtCore import Qt
from PySide2.QtGui import QPen, QColor, QBrush


from ..units import as_mm, as_inch, mm, pt


app = QApplication(['pyside2-backend'])
font_db = QFontDatabase()


class Font:
    def __init__(self, qt_font, metrics):
        self.qt_font = qt_font
        self.metrics = metrics
        self.ascent = metrics.ascent() * 72 / 1200 * pt
        self.descent = metrics.descent() * 72 / 1200 * pt
        self.height = metrics.height() * 72 / 1200 * pt
        self.leading = metrics.lineSpacing() * 72 / 1200 * pt - self.height

    def width_of(self, text):
        return self.metrics.width(text) * 72 / 1200 * pt


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
