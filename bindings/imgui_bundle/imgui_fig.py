import matplotlib
# Important: before importing pyplot, set the renderer to Tk,
# so that the figure is not displayed on the screen before we can capture it.
matplotlib.use('Agg')     #
import matplotlib.pyplot as plt

import numpy
import cv2
import matplotlib
from imgui_bundle.immapp import static
from imgui_bundle import immvision

from typing import Tuple
# from numpy.typing import ArrayLike


"""
Display Matplotlib figures in an ImGui window.
"""


Size = Tuple[int, int]
Point2d = Tuple[float, float]


@static(fig_cache=dict())
def _fig_to_image(figure: matplotlib.figure.Figure, refresh_image: bool = False) -> numpy.ndarray:
    """
    Convert a Matplotlib figure to an RGB image.

    Parameters:
    - figure (matplotlib.figure.Figure): The Matplotlib figure to convert.

    Returns:
    - numpy.ndarray: An RGB image as a NumPy array with uint8 datatype.
    """
    statics = _fig_to_image
    fig_id = id(figure)
    if refresh_image and fig_id in statics.fig_cache:
        del statics.fig_cache[fig_id]
    if fig_id not in statics.fig_cache:
        # draw the renderer
        figure.canvas.draw()
        # Get the RGBA buffer from the figure
        w, h = figure.canvas.get_width_height()
        buf = numpy.fromstring(figure.canvas.tostring_rgb(), dtype=numpy.uint8)
        buf.shape = (h, w, 3)
        img_rgb = cv2.cvtColor(buf, cv2.COLOR_RGB2BGR)
        matplotlib.pyplot.close(figure)
        statics.fig_cache[fig_id] = img_rgb
    return statics.fig_cache[fig_id]


def fig(label_id: str,
        figure: matplotlib.figure.Figure,
        image_display_size: Size = (0, 0),
        refresh_image: bool = False,
        show_options_button: bool = False) -> Point2d:
    """
    Display a Matplotlib figure in an ImGui window.

    Parameters:
    - label_id (str): An identifier for the ImGui image widget.
    - figure (matplotlib.figure.Figure): The Matplotlib figure to display.
    - image_display_size (Size): Size of the displayed image (width, height).
    - refresh_image (bool): Flag to refresh the image.
    - show_options_button (bool): Flag to show additional options.

    Returns:
    - Point2d: The position of the mouse in the image display.

    Important:
        before importing pyplot, set the renderer to Tk,
        so that the figure is not displayed on the screen before we can capture it.
        ```python
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        ```
    """
    image_rgb = _fig_to_image(figure, refresh_image)
    mouse_position = immvision.image_display(label_id, image_rgb, image_display_size, refresh_image, show_options_button)
    return mouse_position
