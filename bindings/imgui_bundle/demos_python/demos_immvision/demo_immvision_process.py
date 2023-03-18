import os.path

import numpy as np
from typing import Any, List
from numpy.typing import NDArray
from enum import Enum
import cv2  # type: ignore
import math

from imgui_bundle.demos_python.demo_utils.api_demos import *
from imgui_bundle import imgui, immvision, immapp, imgui_md
from imgui_bundle.demos_python import demo_utils


ImageRgb = NDArray[np.uint8]
ImageFloat = NDArray[np.floating[Any]]


class Orientation(Enum):
    Horizontal = 0
    Vertical = 1


class SobelParams:
    blur_size = 1.25
    deriv_order = 1  # order of the derivative
    k_size = 7  # size of the extended Sobel kernel it must be 1, 3, 5, or 7 (or -1 for Scharr)
    orientation: Orientation = Orientation.Vertical


def compute_sobel(image: ImageRgb, params: SobelParams) -> ImageFloat:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_float = gray / 255.0
    blurred = cv2.GaussianBlur(img_float, (0, 0), params.blur_size, params.blur_size)

    good_scale = 1.0 / math.pow(2.0, (params.k_size - 2 * params.deriv_order - 2))

    if params.orientation == Orientation.Vertical:
        dx = params.deriv_order
        dy = 0
    else:
        dx = 0
        dy = params.deriv_order
    r = cv2.Sobel(blurred, ddepth=cv2.CV_64F, dx=dx, dy=dy, ksize=params.k_size, scale=good_scale)
    return r


def gui_sobel_params(params: SobelParams) -> bool:
    changed = False

    # Blur size
    imgui.set_next_item_width(immapp.em_size() * 10)
    c, params.blur_size = imgui.slider_float("Blur size", params.blur_size, 0.5, 10)
    if c:
        changed = True
    imgui.same_line()
    imgui.text(" | ")
    imgui.same_line()

    # Deriv order
    imgui.text("Deriv order")
    imgui.same_line()
    for deriv_order in (1, 2, 3, 4):
        c, params.deriv_order = imgui.radio_button(str(deriv_order), params.deriv_order, deriv_order)
        if c:
            changed = True
        imgui.same_line()

    imgui.text(" | ")
    imgui.same_line()

    imgui.text("Orientation")
    imgui.same_line()
    if imgui.radio_button("Horizontal", params.orientation == Orientation.Horizontal):
        changed = True
        params.orientation = Orientation.Horizontal
    imgui.same_line()
    if imgui.radio_button("Vertical", params.orientation == Orientation.Vertical):
        changed = True
        params.orientation = Orientation.Vertical

    return changed


class AppState:
    image: ImageRgb
    image_sobel: ImageFloat
    sobel_params: SobelParams

    immvision_params: immvision.ImageParams
    immvision_params_sobel: immvision.ImageParams

    def __init__(self, image_file: str):
        self.image = cv2.imread(image_file)
        self.sobel_params = SobelParams()
        self.image_sobel = compute_sobel(self.image, self.sobel_params)

        self.immvision_params = immvision.ImageParams()
        self.immvision_params.image_display_size = (350, 0)
        self.immvision_params.zoom_key = "z"

        self.immvision_params_sobel = immvision.ImageParams()
        self.immvision_params_sobel.image_display_size = (350, 0)
        self.immvision_params_sobel.zoom_key = "z"
        self.immvision_params_sobel.show_options_panel = True


@immapp.static(app_state=None)
def demo_gui():
    static = demo_gui

    if static.app_state is None:
        this_dir = os.path.dirname(__file__)
        static.app_state = AppState(this_dir + "/../../demos_assets/images/house.jpg")

    imgui_md.render_unindented(
        """
        This example shows a example of image processing (sobel filter) where you can adjust the params and see their effect in real time. 
        
        Apply Colormaps to the filtered image in the options tab.
        """
    )
    imgui.separator()

    changed = gui_sobel_params(static.app_state.sobel_params)
    if changed:
        static.app_state.image_sobel = compute_sobel(static.app_state.image, static.app_state.sobel_params)
    static.app_state.immvision_params_sobel.refresh_image = changed

    immvision.image("Original", static.app_state.image, static.app_state.immvision_params)
    imgui.same_line()
    immvision.image("Deriv", static.app_state.image_sobel, static.app_state.immvision_params_sobel)


if __name__ == "__main__":
    demo_utils.set_hello_imgui_demo_assets_folder()
    immapp.run_with_markdown(demo_gui, window_size=(1000, 1000))
