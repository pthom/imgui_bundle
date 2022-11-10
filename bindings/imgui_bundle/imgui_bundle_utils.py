from typing import Callable, Any


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
    Use them only in small scripts, not in production code!
    """

    def wrapper(function: Callable[[Any], Any]):
        for key, value in kwargs.items():
            setattr(function, key, value)
        return function

    return wrapper


def run_anon_block(function: Callable[[None], None]):
    """Decorator for anonymous block

    This enables you to emulate CC++ anonymous blocks.
    In the example below, _win_code() is an anonymous block which is evaluated right after its definition.
    Its presence makes it possible to indent parts of the code (for example, the code responsible for the widgets
     inside a window)

        imgui.begin("My window")
        @run_anon_block
        def _win_code():
            imgui.text("What is your name")
            changed_f, first_name = imgui.input_text("First name")
            changed_l, last_name = imgui.input_text("Last name")
            # ...
        imgui.end()

    """
    function()  # type: ignore


from typing import Tuple
import imgui_bundle
from imgui_bundle import hello_imgui
import numpy as np
import cv2 # pip install opencv-python
import PIL.Image  # pip install pillow
from IPython.display import display


VoidFunction = Callable[[None], None]
ScreenSize = Tuple[int, int]


def run_nb(
    gui_function: VoidFunction,
    window_title: str = "",
    window_size_auto: bool = True,
    window_restore_previous_geometry: bool = False,
    window_size: ScreenSize = (0, 0),
    fps_idle: float = 10.0,
    with_implot: bool = True,
    with_markdown: bool = True,
    with_node_editor: bool = True,   
    thumbnail_height = 150,
    thumbnail_ratio = 1.,
    ) -> None:
    """ImguiBundle app runner for jupyter notebook
    
    * This runner will display a thumbnail of the app in the notebook after execution.
    * By default, markdown, implot and node_editor are active.
    * If window_size is left as its default value (0, 0), then the window will autosize
    """
    if window_size[0] > 0 and window_size[1] > 0:
        window_size_auto = False

    imgui_bundle.run(
        gui_function=gui_function,
        window_title=window_title,
        window_size_auto=window_size_auto,
        window_restore_previous_geometry=window_restore_previous_geometry,
        window_size=window_size,
        fps_idle=fps_idle,
        with_implot=with_implot,
        with_markdown=with_markdown,
        with_node_editor=with_node_editor        
    )
    
    from imgui_bundle import hello_imgui
    app_image = hello_imgui.final_app_window_screenshot()
       
    resize_ratio = 1
    if thumbnail_ratio != 1.:
        resize_ratio = thumbnail_ratio
    elif thumbnail_height > 0:
        resize_ratio = thumbnail_height / app_image.shape[0]

    if resize_ratio != 1:
        thumbnail_image = cv2.resize(app_image, (0, 0), fx=resize_ratio, fy=resize_ratio, interpolation=cv2.INTER_AREA)
    else:
        thumbnail_image = app_image
        
    pil_image = PIL.Image.fromarray(thumbnail_image)
    display(pil_image)
