default_backend = None


def get_backend():
    if default_backend is not None:
        return default_backend
    else:
        from . import pyside2
        return pyside2
