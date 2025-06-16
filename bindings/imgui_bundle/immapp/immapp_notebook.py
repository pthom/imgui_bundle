# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
# mypy: disable_error_code=no-untyped-call
from typing import Callable, Tuple
from imgui_bundle import immapp, hello_imgui


GuiFunction = Callable[[], None]
ScreenSize = Tuple[int, int]


def _make_gui_with_light_theme(gui_function: GuiFunction) -> GuiFunction:
    @immapp.static(was_theme_set=False)
    def inner():
        static = inner
        if not static.was_theme_set:
            hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.white_is_white)
            static.was_theme_set = True
        gui_function()
    return inner


def _run_app_function_and_display_image_in_notebook(
        app_function: GuiFunction,  # A function that runs the app entirely
        thumbnail_height: int = 0,
        thumbnail_ratio: float = 0.0,
) -> None:
    """ImguiBundle app runner for jupyter notebook

    This runner is able to:
        * run an ImGui app from a jupyter notebook
        * display a thumbnail of the app + a "run" button in the cell output

    The GUI will be rendered with a white theme.
    If window_size is left as its default value (0, 0), then the window will autosize.

    thumbnail_height and thumbnail_ratio control the size of the screenshot that is displayed after execution.
    """
    # pip install opencv-python or pip install opencv-contrib-python
    import cv2  # type: ignore
    import PIL.Image  # pip install pillow
    from IPython.display import display  # type: ignore

    def make_thumbnail(image):
        resize_ratio = 1.0
        if thumbnail_ratio != 0.0:
            resize_ratio = thumbnail_ratio
        elif thumbnail_height > 0:
            resize_ratio = thumbnail_height / image.shape[0]

        if resize_ratio != 1:
            thumbnail_image = cv2.resize(
                image,
                (0, 0),
                fx=resize_ratio,
                fy=resize_ratio,
                interpolation=cv2.INTER_AREA,
            )
        else:
            thumbnail_image = image
        return thumbnail_image

    # def display_image(image):
    #     pil_image = PIL.Image.fromarray(image)
    #     display(pil_image)

    def display_image(image):
        from IPython.display import Image

        # Convert the input image to a PIL image
        pil_image = PIL.Image.fromarray(image)

        # Save the PIL image to a bytes buffer in PNG format
        import io
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG")
        buffer.seek(0)

        # Create an IPython display Image object and specify PNG format
        jpeg_image = Image(data=buffer.getvalue(), format="jpeg")
        display(jpeg_image)


    def run_app_and_display_thumb():
        nonlocal thumbnail_ratio
        from imgui_bundle import hello_imgui

        app_function()
        app_image = hello_imgui.final_app_window_screenshot()

        scale = hello_imgui.final_app_window_screenshot_framebuffer_scale()
        if thumbnail_ratio == 0.0:
            thumbnail_ratio = 1.0  / scale

        thumbnail = make_thumbnail(app_image)
        display_image(thumbnail)

    run_app_and_display_thumb()


def run_nb(
    gui_function: GuiFunction,
    window_title: str = "",
    window_size_auto: bool = True,
    window_restore_previous_geometry: bool = False,
    window_size: ScreenSize = (0, 0),
    fps_idle: float = 10.0,
    with_implot: bool = True,
    with_markdown: bool = True,
    with_node_editor: bool = True,
    thumbnail_height: int = 0,
    thumbnail_ratio: float = 0.0,
) -> None:
    """ImguiBundle app runner for jupyter notebook

    This runner is able to:
        * run an ImGui app from a jupyter notebook
        * display a thumbnail of the app + a "run" button in the cell output

    The GUI will be rendered with a white theme.
    If window_size is left as its default value (0, 0), then the window will autosize.

    thumbnail_height and thumbnail_ratio control the size of the screenshot that is displayed after execution.
    """
    def run_app():
        nonlocal window_size_auto
        if window_size[0] > 0 and window_size[1] > 0:
            window_size_auto = False

        immapp.run(
            gui_function=_make_gui_with_light_theme(gui_function),
            window_title=window_title,
            window_size_auto=window_size_auto,
            window_restore_previous_geometry=window_restore_previous_geometry,
            window_size=window_size,
            fps_idle=fps_idle,
            with_implot=with_implot,
            with_markdown=with_markdown,
            with_node_editor=with_node_editor,
        )

    _run_app_function_and_display_image_in_notebook(run_app, thumbnail_height, thumbnail_ratio)
