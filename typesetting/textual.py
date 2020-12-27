from .backend import get_backend


def type_face(name):
    backend = get_backend()
    return backend.TypeFace(name)
