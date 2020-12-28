from typesetting import layout as lt
from typesetting.units import mm, pt


@lt.framed()
def definition(word, plural, paragraph, highlight=False):
    title = lt.text_frame(face(15), word)
    info = lt.text_frame(face(12), plural)
    if highlight:
        highlight_pen = renderer.pen(20 * pt, None, fill_color=(255, 255, 50))
        yield title.at(x=5 * mm, y=0 * mm).outline(highlight_pen)
    else:
        yield title.at(x=5 * mm, y=0 * mm)
    yield info.at(x=title.width + 7 * mm, y=1 * mm)

    frame = lt.paragraph(face(8), paragraph, 80 * mm).at(5 * mm, 6 * mm)
    yield frame

    pad = 5 * mm

    yield pen.line_to(0 * mm, frame.y + frame.height + pad).at(2 * mm, 0 * mm)
    yield pen.ellipse(4 * mm, 4 * mm).at(0 * mm, 0.5 * mm)
    yield lt.padding(0 * mm, pad).at(0 * mm, frame.y + frame.height)


def shape_column(description, pen):
    return lt.stack(
        shape_view(
            description + " circle", pen.ellipse(10 * mm, 10 * mm)),
        shape_view(
            description + " rectangle", pen.rectangle(10 * mm, 10 * mm)),
        shape_view(
            description + " line", pen.line_to(10 * mm, 10 * mm)),
        shape_view(
            description + " poly-line", pen.polyline(
                (0 * mm, 0 * mm),
                (7 * mm, 10 * mm),
                (10 * mm, 0 * mm),
                (7 * mm, 3 * mm),
            )),
    )


@lt.framed()
def shape_view(description, shape):
    text = lt.text_frame(face(15), description)
    y = (shape.height - text.height) / 2
    yield text.at(0 * mm, y)
    yield shape.at(30 * mm, 0 * mm).outline(small_pen)


@lt.framed()
def shape_display():
    fill_pen = renderer.pen(20 * pt, (0, 0, 255), fill_color=(255, 255, 0))
    yield shape_column("filled", fill_pen).at(0 * mm, 0 * mm)

    edge_pen = renderer.pen(20 * pt, (0, 255, 0))
    yield shape_column("edged", edge_pen).at(42 * mm, 0 * mm)

    fill_only_pen = renderer.pen(20 * pt, None, fill_color=(255, 0, 255))
    yield shape_column("only fill", fill_only_pen).at(84 * mm, 0 * mm)


@lt.framed()
def header(cw):
    para_w = 140 * mm
    para_x = (cw - para_w) / 2
    yield lt.stack(
        lt.frame(
            pen.line_to(cw - 10 * mm, 0 * mm).at(5 * mm, 5 * mm),
            pen.ellipse(40 * mm, 10 * mm).at(cw / 2 - 20 * mm, 0 * mm),
        ),
        lt.text_frame(face(30), "Summary", center_of=cw),
        lt.paragraph(face(15), (
            "This is a test page, testing the various primitives, which can "
            "then be exported with a backend to verify that this backend is "
            "fully featured and then check that the result looks as "
            "expected."), para_w).at(para_x, 0 * mm),
        pen.polyline(
            (0 * mm, 0 * mm),
            (20 * mm, 10 * mm),
            (cw - 20 * mm, 10 * mm),
            (cw, 0 * mm),
        ),
    )


@lt.page('A4', 10 * mm, 15 * mm)
def page(cw, ch):
    yield header(cw)

    yield lt.center(shape_display(), cw).at(0 * mm, 60 * mm)

    yield lt.image("./res/Quokka_Gary-Houston_CC-0.jpg", 80 * mm).at(x=0 * mm, y=120 * mm)
    yield lt.stack(
        definition("quoit", "(plural quoits)",
                   ("1) A flat disc of metal or stone thrown at a target in the game of quoits. "
                    "2) A ring of rubber or rope similarly used in the game of deck-quoits. "
                    "3) The flat stone covering a cromlech. "
                    "4) The discus used in ancient sports.")),
        definition("quokka", "(plural quokkas)",
                   "A cat-sized marsupial, Setonix brachyurus, of southwestern Australia.",
                   highlight=True),
        definition("quorum", "(plural quorums or quora)",
                   ("1) The minimum number of members required for a group to "
                    "officially conduct business and to cast votes, often but "
                    "not necessarily a majority or supermajority. "
                    "‟We can discuss the issue tonight, but cannot vote until we "
                    "have a quorum”. "
                    "2) A selected body of persons.")),
    ).at(85 * mm, 120 * mm).outline(small_pen)

    # QQQ crop


if __name__ == '__main__':
    renderer = lt.renderer("out/pyside2.pdf")
    face = renderer.type_face("Adobe Arabic")
    pen = renderer.pen(20 * pt, fill_color=(255, 255, 255))
    small_pen = renderer.pen(10 * pt, color=(150, 150, 150))
    renderer.render(page(), debug=True)
