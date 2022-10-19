from typing import Any, Callable, Optional
from imgui_bundle import implot, imgui_node_editor


class ImplotContextHolder:
    """Utility to simplify the management of the lifetime of the implot context
    Simply call ImplotContextHolder.start() at the start of the application,
    and it will initialize a context that will be present for the rest of the app lifetime.

    In bigger applications, it is advised to use the standard way,
    i.e. call yourself implot.create_context() and implot.destroy_context() when needed
    """

    def __init__(self):
        implot.create_context()

    def __del__(self):
        implot.destroy_context()

    @staticmethod
    def _instance():  # type: ignore
        if not hasattr(ImplotContextHolder._instance, "_inst"):
            ImplotContextHolder._instance._inst = ImplotContextHolder()
        return ImplotContextHolder._instance._inst

    @staticmethod
    def start():
        _ = ImplotContextHolder._instance()


class ImguiNodeEditorContextHolder:
    """Utility class to simplify the management of the lifetime of the imgui_node_editor context
    Simply call:
        - ImguiNodeEditorContextHolder.start() at the start of the application
        - ImguiNodeEditorContextHolder.set_as_current_editor() at each frame
    The context will be destroyed when the app exits.

    In bigger applications, it is advised to use the standard way,
    i.e. call yourself imgui_node_editor.create_editor, imgui_node_editor.destroy_editor,
    and imgui_node_editor.set_current_editor when needed
    """

    _context: imgui_node_editor.EditorContext

    def __init__(self, config: Optional[imgui_node_editor.Config]):
        self._context = imgui_node_editor.create_editor(config)

    def __del__(self):
        imgui_node_editor.destroy_editor(self._context)

    @staticmethod
    def _instance(config: Optional[imgui_node_editor.Config] = None):  # type: ignore
        if not hasattr(ImguiNodeEditorContextHolder._instance, "_inst"):
            ImguiNodeEditorContextHolder._instance._inst = ImguiNodeEditorContextHolder(config)
        return ImguiNodeEditorContextHolder._instance._inst

    @staticmethod
    def start(config: Optional[imgui_node_editor.Config] = None):
        _ = ImguiNodeEditorContextHolder._instance(config)

    @staticmethod
    def set_as_current_editor():
        instance = ImguiNodeEditorContextHolder._instance()
        imgui_node_editor.set_current_editor(instance._context)


def static(**kwargs):
    """A decorator that adds static variables to a function
    :param kwargs: list of static variables to add
    :return: decorated function

    Example:
        @static(x=0)
        def f():
            f.x += 1
            print(f.x)

        invoking f three times would print 1, 2, 3.
    """
    def wrapper(function: Callable[[Any], Any]):
        for key, value in kwargs.items():
            setattr(function, key, value)
        return function
    return wrapper
