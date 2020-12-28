from typesetting import layout as lt
from typesetting.units import mm, pt


@lt.framed()
def time_slot(title, when, where, paragraph):
    title = lt.text_frame(face(15), title)
    info = lt.text_frame(face(12), when + ", " + where)
    yield title.at(x=5 * mm, y=0 * mm)
    yield info.at(x=title.width + 7 * mm, y=1 * mm)

    frame = lt.paragraph(face(8), paragraph, 115 * mm).at(5 * mm, 6 * mm)
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


@lt.page('A4', 10 * mm, 15 * mm)
def page():
    yield pen.rectangle(40 * mm, 50 * mm)
    yield lt.stack(
        lt.text_frame(face(12), "Summary"),
        lt.paragraph(face(10), (
            "Experienced from a large number of hardware and software related projects and "
            "involved in many different fields: system development, architecture development "
            "and specification, requirement specification, system modeling, verification and "
            "test, integration, processor development, application development, synthesis, "
            "static timing verification, backend with place and route, EDA and environment "
            "responsibility."), 150 * mm),
    ).at(45 * mm, 0 * mm)

    yield lt.stack(
        time_slot("Integration of WLAN-module in CAN product", "2007", "Assignment at: Kvaser AB",
                  ("Integrating the BG211W WLAN module to a M32C/87 microcontroller. Extending "
                   "debug functionality and logging to include http channel. General functional "
                   "development and debugging.")),
        time_slot("ASIC for biometric application", "2006", "Assignment at: Fingerprints Card AB",
                  ("Designing ASIC with 8051 processor and digital signal processing hardware for "
                   "algorithmic acceleration.  System verification was done on FPGA platform with "
                   "production C-code. The ASIC was tested with self checking assembler test cases, "
                   "also producing production test vectors. Implemented in TSMC technology.")),
    ).at(60 * mm, 55 * mm).outline(small_pen)

    yield shape_display().at(0 * mm, 100 * mm)

    yield lt.image("./res/Quokka_Gary-Houston_CC-0.jpg", 100 * mm).at(x=0 * mm, y=150 * mm)
    # QQQ crop


if __name__ == '__main__':
    renderer = lt.renderer("out/pyside2.pdf")
    face = renderer.type_face("Adobe Arabic")
    pen = renderer.pen(20 * pt, fill_color=(255, 255, 255))
    small_pen = renderer.pen(10 * pt, color=(150, 150, 150))
    renderer.render(page(), debug=True)
