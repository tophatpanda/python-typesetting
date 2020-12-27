from typesetting import layout as lt
from typesetting import textual
from typesetting.units import mm


face = textual.type_face("Adobe Arabic")


@lt.centered(210 * mm, 297 * mm)
@lt.framed(180 * mm, 277 * mm)
def page():
    yield lt.rectangle(40 * mm, 50 * mm)
    yield lt.text_frame(face(12), "Summary").at(45 * mm, 0 * mm)


if __name__ == '__main__':
    lt.prepare("out/pyside2.pdf", [face])(page())
