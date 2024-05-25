"""imgui_fig.fig: Display Matplotlib figures in an ImGui window.

Important: before importing pyplot, set the renderer to Tk,
so that the figure is not displayed on the screen before we can capture it.
"""
import matplotlib
matplotlib.use('Agg')     #
import matplotlib.pyplot as plt

import numpy
import cv2
import matplotlib
from imgui_bundle.immapp import static
from imgui_bundle import immvision, ImVec2, imgui


@static(fig_image_cache=dict())
def _fig_to_image(label_id: str, figure: matplotlib.figure.Figure, refresh_image: bool = False) -> numpy.ndarray:
    """
    Convert a Matplotlib figure to an RGB image.

    Parameters:
    - figure (matplotlib.figure.Figure): The Matplotlib figure to convert.

    Returns:
    - numpy.ndarray: An RGB image as a NumPy array with uint8 datatype.
    """
    statics = _fig_to_image
    fig_id = imgui.get_id(label_id)
    if refresh_image and fig_id in statics.fig_image_cache:
        del statics.fig_image_cache[fig_id]
    if fig_id not in statics.fig_image_cache:
        # draw the renderer
        figure.canvas.draw()
        # Get the RGBA buffer from the figure
        w, h = figure.canvas.get_width_height()
        buf = numpy.fromstring(figure.canvas.tostring_rgb(), dtype=numpy.uint8)
        buf.shape = (h, w, 3)
        img_rgb = cv2.cvtColor(buf, cv2.COLOR_RGB2BGR)
        matplotlib.pyplot.close(figure)
        statics.fig_image_cache[fig_id] = img_rgb
    return statics.fig_image_cache[fig_id]



def fig(label_id: str,
        figure: matplotlib.figure.Figure,
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

    Important:
        before importing pyplot, set the renderer to Tk,
        so that the figure is not displayed on the screen before we can capture it.
        ```python
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        ```
    """
    image_rgb = _fig_to_image(label_id, figure, refresh_image)

    mouse_position_tuple = immvision.image_display_resizable(
        label_id, image_rgb, size, refresh_image, resizable, show_options_button)
    mouse_position = ImVec2(mouse_position_tuple[0], mouse_position_tuple[1])
    return mouse_position
