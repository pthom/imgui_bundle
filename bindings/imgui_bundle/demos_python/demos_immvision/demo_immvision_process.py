"""ImmVision: an image processing pipeline, tuned live

A Sobel filter on a photo: change the blur, the derivative's order and its orientation, and the result updates at
once. The original and the filtered image share a zoom key, so they pan and zoom together; the options panel of the
filtered image applies colormaps. A button downloads a random photo. The processing is OpenCV's
(`pip install imgui-bundle[imgproc]`), the display ImmVision's.
"""
import numpy as np
from typing import Any, Optional
from numpy.typing import NDArray
from enum import Enum
import cv2
import math

from imgui_bundle import imgui, immvision, immapp, rich_md, hello_imgui, register_demos_assets_folder

register_demos_assets_folder()

RANDOM_PHOTO_URL = "https://picsum.photos/640/480"  # a different photo at each download
NARROW_WIDTH_EM = 46  # Under this width (in em, a phone), the controls and the images go one under the other

ImageRgb = NDArray[np.uint8]
ImageFloat = NDArray[np.floating[Any]]


class SobelParams:
    """The parameters for our image processing pipeline"""

    class Orientation(Enum):
        Horizontal = 0
        Vertical = 1

    blur_size = 1.25
    deriv_order = 1  # order of the derivative
    k_size = 7  # size of the extended Sobel kernel it must be 1, 3, 5, or 7 (or -1 for Scharr)
    orientation: Orientation = Orientation.Vertical


def compute_sobel(image: ImageRgb, params: SobelParams) -> ImageFloat:
    """Our image processing pipeline"""
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    img_float = gray / 255.0
    blurred = cv2.GaussianBlur(
        img_float, (0, 0), sigmaX=params.blur_size, sigmaY=params.blur_size  # type: ignore
    )

    good_scale = 1.0 / math.pow(2.0, (params.k_size - 2 * params.deriv_order - 2))

    if params.orientation == SobelParams.Orientation.Vertical:
        dx = params.deriv_order
        dy = 0
    else:
        dx = 0
        dy = params.deriv_order
    r = cv2.Sobel(
        blurred, ddepth=cv2.CV_64F, dx=dx, dy=dy, ksize=params.k_size, scale=good_scale
    )
    return r  # type: ignore


def next_controls(narrow: bool):
    """Between two groups of controls: a separator on the same line, or a new line on a narrow screen"""
    if not narrow:
        imgui.same_line()
        imgui.text(" | ")
        imgui.same_line()


def gui_sobel_params(params: SobelParams, narrow: bool) -> bool:
    """A GUI to edit the parameters for our image processing pipeline"""
    changed = False

    # Blur size
    imgui.set_next_item_width(immapp.em_size() * 10)
    c, params.blur_size = imgui.slider_float("Blur size", params.blur_size, 0.5, 10)
    if c:
        changed = True
    next_controls(narrow)

    # Deriv order
    imgui.text("Deriv order")
    imgui.same_line()
    for deriv_order in (1, 2, 3, 4):
        c, params.deriv_order = imgui.radio_button(
            str(deriv_order), params.deriv_order, deriv_order
        )
        if c:
            changed = True
        if deriv_order < 4:
            imgui.same_line()
    next_controls(narrow)

    imgui.text("Orientation")
    imgui.same_line()
    if imgui.radio_button(
        "Horizontal", params.orientation == SobelParams.Orientation.Horizontal
    ):
        changed = True
        params.orientation = SobelParams.Orientation.Horizontal
    imgui.same_line()
    if imgui.radio_button(
        "Vertical", params.orientation == SobelParams.Orientation.Vertical
    ):
        changed = True
        params.orientation = SobelParams.Orientation.Vertical

    return changed


# Our Application State contains:
#     - the original & processed image (image & imageSobel)
#     - our parameters for the processing pipeline (sobelParams)
#     - parameters to display the images via ImmVision: they share the same zoom key,
#       so that we can move the two image in sync
class AppState:
    image: ImageRgb
    image_sobel: ImageFloat
    sobel_params: SobelParams

    immvision_params: immvision.ImageParams
    immvision_params_sobel: immvision.ImageParams

    def __init__(self, image_file: str):
        # In RGB: ImmVision's default order (OpenCV reads BGR)
        self.image = cv2.cvtColor(cv2.imread(image_file), cv2.COLOR_BGR2RGB)  # type: ignore[arg-type, assignment]
        self.sobel_params = SobelParams()
        self.image_sobel = compute_sobel(self.image, self.sobel_params)
        self.download: Optional[immapp.Download] = None  # the download of a random photo, in the background

        self.immvision_params = immvision.ImageParams()
        self.immvision_params.zoom_key = "z"

        self.immvision_params_sobel = immvision.ImageParams()
        self.immvision_params_sobel.zoom_key = "z"
        self.immvision_params_sobel.show_options_panel = True
        self.was_narrow: Optional[bool] = None  # the layout of the last frame

    def fit_layout(self, narrow: bool):
        """The images side by side, 22 em wide; on a narrow screen (a phone), at the window's width (a negative width),
        and the options of the filtered image in a window of their own. Set when the layout changes only: the user may
        resize the images in between."""
        if narrow == self.was_narrow:
            return
        self.was_narrow = narrow
        size = (-1, 0) if narrow else (int(immapp.em_size(22)), 0)
        self.immvision_params.image_display_size = size
        self.immvision_params_sobel.image_display_size = size
        self.immvision_params_sobel.show_options_in_tooltip = narrow


def take_downloaded_photo(state: AppState) -> bool:
    """Makes the downloaded photo the image, once its download is done (a failure keeps the image as is)"""
    if state.download is None or not state.download.done:
        return False
    download, state.download = state.download, None
    if download.error:
        return False
    decoded = cv2.imdecode(np.frombuffer(download.data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if decoded is None:
        return False
    state.image = cv2.cvtColor(decoded, cv2.COLOR_BGR2RGB)  # type: ignore[assignment]
    return True


# Our GUI function
#    (which instantiates a static app state at startup)
@immapp.static(app_state=None)
def gui():
    static = gui

    if static.app_state is None:
        static.app_state = AppState(hello_imgui.asset_file_full_path("images/house.jpg"))

    rich_md.render(
        """
        An image processing pipeline (a Sobel filter): adjust its parameters, and see their effect in real time.

        * Pan and zoom the image with the mouse and the mouse wheel
        * Apply Colormaps to the filtered image in the options tab.
        """
    )
    imgui.separator()

    narrow = imgui.get_content_region_avail().x < immapp.em_size(NARROW_WIDTH_EM)
    changed = gui_sobel_params(static.app_state.sobel_params, narrow)
    if not narrow:
        imgui.same_line(spacing=immapp.em_size(3))
    if imgui.button("Random photo"):
        # The download runs in the background (the GUI stays responsive): take_downloaded_photo() takes its result
        static.app_state.download = immapp.start_download(RANDOM_PHOTO_URL)
    new_image = take_downloaded_photo(static.app_state)
    if changed or new_image:
        static.app_state.image_sobel = compute_sobel(
            static.app_state.image, static.app_state.sobel_params
        )
    static.app_state.immvision_params.refresh_image = new_image
    static.app_state.immvision_params_sobel.refresh_image = changed or new_image

    static.app_state.fit_layout(narrow)
    immvision.image(
        "Original", static.app_state.image, static.app_state.immvision_params
    )
    if not narrow:
        imgui.same_line()
    immvision.image(
        "Deriv", static.app_state.image_sobel, static.app_state.immvision_params_sobel
    )


def main():
    immapp.run_with_markdown(gui, window_size=(1000, 1000))


# The main entry point will run our GUI function
if __name__ == "__main__":
    main()
