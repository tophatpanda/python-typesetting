from typesetting import document as doc
from typesetting import composing as c
from typesetting import knuth
from typesetting.pyside2_backend import get_fonts
from typesetting.skeleton import frame_layout, unroll
from PySide2.QtCore import QSizeF, Qt, QPoint, QMarginsF
from PySide2.QtGui import QPainter, QPdfWriter, QFontDatabase, QPen


mm = 72 / 25.4

story = []

with open("dagon.txt", "r", encoding="utf8") as f:
    for line in f:
        if line:
            story.append((c.avoid_widows_and_orphans,))
            story.append((
                knuth.knuth_paragraph, 0, 0, [('roman', line.rstrip())]))

renderer = doc.Renderer(210, 297)
fonts = get_fonts(renderer.painter, [
    ('bold', 'Gentium Basic', 'Bold', 8),
    ('roman', 'Gentium Basic', 'Roman', 8),
])

frames = [
    # left, top, width, height
    (25, 25, 90, 145),
    (120, 105, 80, 90),
    (25, 200, 165, 30),
    (30, 235, 40, 25),
    (110, 235, 75, 40),
]
# add unit to all numbers
frames = [
    (l * mm, t * mm, w * mm, h * mm) for (l, t, w, h)
    in frames]
next_line = frame_layout(frames, 210, 297)


def mark_frames(painter, frames):
    pen = QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)
    for l, t, w, h in frames:
        pt = 1200 / 72.0
        points = [QPoint(x * pt, y * pt) for x, y in
                  [(l, t), (l + w, t), (l + w, t + h), (l, t + h)]]
        for i in range(len(points)):
            painter.drawLine(points[i], points[(i + 1) % len(points)])


lines = unroll(None, c.run(story, fonts, None, next_line))
page = None
mark_frames(renderer.painter, frames)

for line in lines:
    if line is None:
        continue
    if page is not None and page is not line.column.page:
        renderer.new_page()
        mark_frames(renderer.painter, frames)
    page = line.column.page

    for graphic in line.graphics:
        function, *args = graphic
        function(fonts, line, renderer.painter, *args)

renderer.painter.end()
