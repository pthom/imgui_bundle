from typing import Any, Callable, Optional
from imgui_bundle import implot, imgui_node_editor, hello_imgui, imgui, imgui_md


VoidFunction = Callable[[None], None]


_NODE_EDITOR_CONTEXT: Optional[imgui_node_editor.EditorContext] = None


def run(
        gui_fonction: Optional[VoidFunction] = None,
        window_size: Optional[imgui.ImVec2] = None,
        window_title: str = "",
        runner_params: Optional[hello_imgui.RunnerParams] = None,
        with_implot: bool = False,
        with_node_editor: bool = False,
        with_node_editor_config: Optional[imgui_node_editor.Config] = None,
        with_markdown: bool = False,
        with_markdown_options: Optional[imgui_md.MarkdownOptions] = None
) -> None:
    """Helper to run an hello_imgui app for imgui_bundle:

        - You can specify your gui code either via `gui_function` or via `runner_params`
        - if `with_markdown` or `with_markdown_options` is specified, then  the markdown context will be initialized
          (i.e. required fonts will be loaded)
        - if `with_implot` is True, then a context for implot will be created/destroyed automatically
        - if `with_node_editor` or with_node_editor_config` is specified, then a context for imgui_node_editor
          will be created automatically.
    """

    global _NODE_EDITOR_CONTEXT

    # instantiate runner_params and set gui functio
    if runner_params is None:
        runner_params = hello_imgui.RunnerParams()
    if gui_fonction is not None:
        runner_params.callbacks.show_gui = gui_fonction
    if window_size is not None:
        runner_params.app_window_params.window_size = window_size;
    if len(window_title) > 0:
        runner_params.app_window_params.window_title = window_title;

    # create implot context if required
    if with_implot:
        implot.create_context()

    # create imgui_node_editor context if required
    if with_node_editor or with_node_editor_config is not None:
        with_node_editor = True
        if with_node_editor_config is None:
            with_node_editor_config = imgui_node_editor.Config()
        _NODE_EDITOR_CONTEXT = imgui_node_editor.create_editor(with_node_editor_config)
        imgui_node_editor.set_current_editor(_NODE_EDITOR_CONTEXT)

    # load markdown fonts if needed
    if with_markdown or with_markdown_options is not None:
        with_markdown = True
        if with_markdown_options is None:
            with_markdown_options = imgui_md.MarkdownOptions()
        imgui_md.initialize_markdown(with_markdown_options)
        runner_params.callbacks.load_additional_fonts = imgui_md.get_font_loader_function()

    hello_imgui.run(runner_params)

    if with_implot:
        implot.destroy_context()

    if with_node_editor:
        imgui_node_editor.destroy_editor(_NODE_EDITOR_CONTEXT)
        _NODE_EDITOR_CONTEXT = None


def current_node_editor_context() -> imgui_node_editor.EditorContext:
    if _NODE_EDITOR_CONTEXT is None:
        raise RuntimeError("""No current node editor context
        Did you set with_node_editor_config when calling imgui_bundle.run()?""")
    return _NODE_EDITOR_CONTEXT


def static(**kwargs):
    """A decorator that adds static variables to a function
    :param kwargs: list of static variables to add
    :return: decorated function

    Example:
        @static(x=0, y=0)
        def my_function():
            # static vars are stored as attributes of "my_function"
            # we use static as a more readable synonym.
            static = my_function

            static.x += 1
            static.y += 2
            print(f"{static.f.x}, {static.f.x}")

        invoking f three times would print 1, 2 then 2, 4, then 3, 6

    Static variables are similar to global variables, with the same shortcomings!
    Use them only in small scripts, never in production code!
    """

    def wrapper(function: Callable[[Any], Any]):
        for key, value in kwargs.items():
            setattr(function, key, value)
        return function

    return wrapper
