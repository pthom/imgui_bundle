# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
# mypy: disable_error_code=no-untyped-call
from typing import Optional, Callable, Tuple
from imgui_bundle import immapp, hello_imgui
import imgui_bundle


GuiFunction = Callable[[], None]
ScreenSize = Tuple[int, int]


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
    thumbnail_height: int = 150,
    thumbnail_ratio: float = 0.0,
    run_id: Optional[str] = None,
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
    from IPython.core.display import HTML  # type: ignore

    def run_app():
        nonlocal window_size_auto
        if window_size[0] > 0 and window_size[1] > 0:
            window_size_auto = False

        @immapp.static(was_theme_set=False)
        def gui_with_light_theme():
            static = gui_with_light_theme
            if not static.was_theme_set:
                hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.white_is_white)
                static.was_theme_set = True
            gui_function()

        immapp.run(
            gui_function=gui_with_light_theme,
            window_title=window_title,
            window_size_auto=window_size_auto,
            window_restore_previous_geometry=window_restore_previous_geometry,
            window_size=window_size,
            fps_idle=fps_idle,
            with_implot=with_implot,
            with_markdown=with_markdown,
            with_node_editor=with_node_editor,
        )

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

    def display_image(image):
        pil_image = PIL.Image.fromarray(image)
        display(pil_image)

    def run_app_and_display_thumb():
        from imgui_bundle import hello_imgui

        run_app()
        app_image = hello_imgui.final_app_window_screenshot()
        thumbnail = make_thumbnail(app_image)
        display_image(thumbnail)

    def display_run_button():
        html_code = f"""
        <script>
        function btnClick_{run_id}(btn) {{
            // alert("btnClick_{run_id}");
            cell_element = btn.parentElement.parentElement.parentElement.parentElement.parentElement;
            cell_idx = Jupyter.notebook.get_cell_elements().index(cell_element)
            IPython.notebook.kernel.execute("imgui_bundle.JAVASCRIPT_RUN_ID='{run_id}'")
            Jupyter.notebook.execute_cells([cell_idx])
        }}
        </script>
        <button onClick="btnClick_{run_id}(this)">Run</button>
        """
        display(HTML(html_code))

    def display_app_with_run_button(run_id):
        """Experiment displaying a "run" button in the notebook below the screenshot. Disabled as of now
        If using this, it would be possible to run the app only if the user clicks on the Run button
        (and not during normal cell execution).
        """
        if run_id is None:
            run_app_and_display_thumb()
        else:
            if hasattr(imgui_bundle, "JAVASCRIPT_RUN_ID"):
                print(
                    "imgui_bundle.JAVASCRIPT_RUN_ID="
                    + imgui_bundle.JAVASCRIPT_RUN_ID
                    + "{run_id=}"
                )
                if imgui_bundle.JAVASCRIPT_RUN_ID == run_id:
                    run_app_and_display_thumb()
            else:
                print("imgui_bundle: no JAVASCRIPT_RUN_ID")

    # display_app_with_run_button(run_id)
    run_app_and_display_thumb()
