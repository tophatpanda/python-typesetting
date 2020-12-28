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
    yield pen.ellipse(4 * mm, 4 * mm, (255, 255, 255)).at(0 * mm, 0.5 * mm)
    yield lt.padding(0 * mm, pad).at(0 * mm, frame.y + frame.height)


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
    ).at(60 * mm, 55 * mm)

    yield lt.image("./res/Quokka_Gary-Houston_CC-0.jpg", 100 * mm).at(x=0 * mm, y=150 * mm)
    # QQQ crop


if __name__ == '__main__':
    renderer = lt.renderer("out/pyside2.pdf")
    face = renderer.type_face("Adobe Arabic")
    pen = renderer.pen(20 * pt, fill_color=(255, 255, 255))
    renderer.render(page(), debug=True)
