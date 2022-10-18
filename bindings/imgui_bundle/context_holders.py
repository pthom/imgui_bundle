from imgui_bundle import implot
from typing import Optional


class _ImplotContextHolder:
    def __init__(self):
        implot.create_context()

    def __del__(self):
        implot.destroy_context()


_IMPLOT_CTX_HOLDER: Optional[_ImplotContextHolder] = None


def implot_create_global_context() -> None:
    """Utility to simplify the management of the lifetime of the implot context
    Simply call this function, and it will initialize a context that will be present
    for the rest of the app lifetime
    """
    global _IMPLOT_CTX_HOLDER
    if _IMPLOT_CTX_HOLDER is None:
        _IMPLOT_CTX_HOLDER = _ImplotContextHolder()
    else:
        import logging
        logging.warning("Second call of implot_create_global_context()!")
