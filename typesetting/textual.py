from .backend import get_backend


def type_face(name):
    backend = get_backend()
    return backend.TypeFace(name)


def naive_wrap(font, string, width):
    x = 0
    line = []
    space = font.width_of(' ')
    for word in string.split():
        x = x + font.width_of(word) + space
        if x > width:
            yield line
            line = []
            x = font.width_of(word)
        line.append(word)
    yield line
