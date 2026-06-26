"""imgui_fig.fig: Display Matplotlib figures in an ImGui window.
"""

# Note: since 1.92.9, no need to call matplotlib.use('Agg') anymore: imgui_fig renders figures offscreen via a dedicated Agg canvas.

from imgui_bundle.immapp import static  # noqa: E402
from imgui_bundle import immvision, ImVec2, imgui  # noqa: E402
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    import matplotlib.figure
    from numpy.typing import NDArray


@static(fig_image_cache=dict())
def _fig_to_image(label_id: str, figure: "matplotlib.figure.Figure", refresh_image: bool = False) -> "NDArray[np.uint8]":
    """
    Convert a Matplotlib figure to an RGB image.

    Parameters:
    - figure (matplotlib.figure.Figure): The Matplotlib figure to convert.

    Returns:
    - numpy.ndarray: An RGB image as a NumPy array with uint8 datatype.
    """
    import numpy  # noqa: E402
    from matplotlib.backends.backend_agg import FigureCanvasAgg  # noqa: E402

    statics = _fig_to_image
    fig_id = imgui.get_id(label_id)
    if refresh_image and fig_id in statics.fig_image_cache:
        del statics.fig_image_cache[fig_id]
    if fig_id not in statics.fig_image_cache:
        canvas = figure.canvas
        # Make sure we can read an RGBA buffer, regardless of the active matplotlib
        # backend (no need for matplotlib.use('Agg')). Most Agg-based canvases (incl.
        # the macOS one) already provide buffer_rgba(); only swap in a fresh Agg canvas
        # if the current one cannot.
        if not hasattr(canvas, "buffer_rgba"):
            canvas = FigureCanvasAgg(figure)  # the constructor attaches itself as figure.canvas
        # Interactive backends bump the figure dpi on HiDPI screens (e.g. macOS retina
        # renders at device_pixel_ratio 2 -> a 2x larger buffer). Reset it to 1 so the
        # captured image keeps its logical size.
        ratio = getattr(canvas, "device_pixel_ratio", 1)
        if ratio != 1 and hasattr(canvas, "_set_device_pixel_ratio"):
            canvas._set_device_pixel_ratio(1)
        # draw the renderer, then grab the RGBA buffer (already shaped as (h, w, 4)).
        canvas.draw()
        statics.fig_image_cache[fig_id] = numpy.asarray(canvas.buffer_rgba())

    return statics.fig_image_cache[fig_id]  # type: ignore




def fig(label_id: str,
        figure: "matplotlib.figure.Figure",
        size: ImVec2 | None = None,
        refresh_image: bool = False,
        resizable: bool = True,
        show_options_button: bool = False) -> ImVec2:
    """
    Display a Matplotlib figure in an ImGui window.

    Parameters:
    - label_id (str): An identifier for the ImGui image widget.
    - figure (matplotlib.figure.Figure): The Matplotlib figure to display.
    - size (Size): Size of the displayed fig
                   Will be updated if resizable is True
    - refresh_image (bool): Flag to refresh the image.
    - show_options_button (bool): Flag to show additional options.

    Returns:
    - The position of the mouse in the figure
    """
    image_rgb = _fig_to_image(label_id, figure, refresh_image)

    immvision.push_color_order_rgb()
    mouse_position_tuple = immvision.image_display_resizable(
        label_id, image_rgb, size, refresh_image, resizable, show_options_button)
    immvision.pop_color_order()
    mouse_position = ImVec2(mouse_position_tuple[0], mouse_position_tuple[1])
    return mouse_position
