"""# ImmVision: Image Inspection

[ImmVision](https://github.com/pthom/immvision) is an image debugger for Dear ImGui with zoom, pan, pixel inspection, and colormaps.

This demo downloads an image, applies a Sobel edge filter (using OpenCV), and displays both side by side with **linked zoom** - pan one image, the other follows.

**Try it:**
- Drag to pan, scroll to zoom
- Adjust blur and derivative order
- Open the "Options" panel on the filtered image to try colormaps
- Each run downloads a different random photo

**Links:**
- [ImmVision repository](https://github.com/pthom/immvision)
"""
import math
import numpy as np
from enum import Enum
from imgui_bundle import (
    imgui, immvision, immapp, hello_imgui,
)

# Download image using Pyodide's top-level await
# (this code is exec'd by Pyodide's runPythonAsync)
import cv2  # type: ignore
from pyodide.http import pyfetch  # type: ignore
_IMAGE_URL = "https://picsum.photos/640/480"
_resp = await pyfetch(_IMAGE_URL)
_bytes = await _resp.bytes()
_loaded_image = cv2.imdecode(
    np.frombuffer(_bytes, dtype=np.uint8),
    cv2.IMREAD_COLOR)

immvision.use_rgb_color_order()


class SobelParams:
    """Parameters for the Sobel edge filter."""
    class Orientation(Enum):
        Horizontal = 0
        Vertical = 1
    blur_size: float = 1.25
    deriv_order: int = 1
    k_size: int = 7
    orientation: Orientation = Orientation.Vertical


def compute_sobel(image, params: SobelParams):
    """Apply Sobel edge detection."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(
        gray / 255.0, (0, 0),
        sigmaX=params.blur_size,
        sigmaY=params.blur_size)
    scale = 1.0 / math.pow(
        2.0, params.k_size - 2 * params.deriv_order - 2)
    dx = params.deriv_order if params.orientation == SobelParams.Orientation.Vertical else 0
    dy = 0 if dx > 0 else params.deriv_order
    return cv2.Sobel(
        blurred, ddepth=cv2.CV_64F,
        dx=dx, dy=dy,
        ksize=params.k_size, scale=scale)


class AppState:
    def __init__(self, image):
        self.image = image
        self.sobel_params = SobelParams()
        self.image_sobel = compute_sobel(
            image, self.sobel_params)
        # ImmVision display params
        # zoom_key links both images (synced pan/zoom)
        disp_w = int(hello_imgui.em_size(20))
        self.params = immvision.ImageParams()
        self.params.image_display_size = (disp_w, 0)
        self.params.zoom_key = "z"
        self.params_sobel = immvision.ImageParams()
        self.params_sobel.image_display_size = (disp_w, 0)
        self.params_sobel.zoom_key = "z"
        self.params_sobel.show_options_panel = True


def gui_sobel_params(p: SobelParams) -> bool:
    """GUI for Sobel filter parameters. Returns True if changed."""
    changed = False
    em = hello_imgui.em_size()
    # Blur
    imgui.set_next_item_width(em * 8)
    c, p.blur_size = imgui.slider_float(
        "Blur", p.blur_size, 0.5, 10)
    changed = changed or c
    imgui.same_line()
    # Deriv order
    imgui.text("Order:")
    imgui.same_line()
    for order in (1, 2, 3, 4):
        c, p.deriv_order = imgui.radio_button(
            str(order), p.deriv_order, order)
        changed = changed or c
        imgui.same_line()
    # Orientation
    imgui.text("  Dir:")
    imgui.same_line()
    O = SobelParams.Orientation
    if imgui.radio_button("H", p.orientation == O.Horizontal):
        p.orientation = O.Horizontal
        changed = True
    imgui.same_line()
    if imgui.radio_button("V", p.orientation == O.Vertical):
        p.orientation = O.Vertical
        changed = True
    return changed


def gui(state: AppState) -> None:
    s = state

    # Documentation panel
    immapp.render_markdown_doc_panel(__doc__, height_em=12)

    # Sobel parameters
    changed = gui_sobel_params(s.sobel_params)
    if changed:
        s.image_sobel = compute_sobel(
            s.image, s.sobel_params)
    s.params_sobel.refresh_image = changed

    # Display both images side by side
    immvision.image("Original", s.image, s.params)
    imgui.same_line()
    immvision.image("Sobel", s.image_sobel, s.params_sobel)


def main():
    state = AppState(_loaded_image)
    immapp.run(
        lambda: gui(state),
        window_size=(1000, 700),
        window_title="ImmVision: Image Inspection",
        with_markdown=True,
        fps_idle=0)


if __name__ == "__main__":
    main()
