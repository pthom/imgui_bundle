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


def gui_sobel_params(params: SobelParams) -> bool:
    """A GUI to edit the parameters for our image processing pipeline"""
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
        c, params.deriv_order = imgui.radio_button(
            str(deriv_order), params.deriv_order, deriv_order
        )
        if c:
            changed = True
        imgui.same_line()

    imgui.text(" | ")
    imgui.same_line()

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
        self.downloaded: Optional[bytes] = None  # a random photo, once its download (in the background) is done

        self.immvision_params = immvision.ImageParams()
        self.immvision_params.image_display_size = (int(immapp.em_size(22)), 0)
        self.immvision_params.zoom_key = "z"

        self.immvision_params_sobel = immvision.ImageParams()
        self.immvision_params_sobel.image_display_size = (int(immapp.em_size(22)), 0)
        self.immvision_params_sobel.zoom_key = "z"
        self.immvision_params_sobel.show_options_panel = True


def download_random_photo(state: AppState) -> None:
    """Starts a download: synchronous on the desktop (a short wait), asynchronous in Pyodide (a GUI callback cannot
    await: the photo lands in state.downloaded, and the next frame takes it)"""
    from imgui_bundle import __bundle_pyodide__
    if __bundle_pyodide__:
        import asyncio

        async def download() -> None:
            state.downloaded = await immapp.download_url_bytes_async(RANDOM_PHOTO_URL)
        asyncio.ensure_future(download())
    else:
        state.downloaded = immapp.download_url_bytes(RANDOM_PHOTO_URL)


def take_downloaded_photo(state: AppState) -> bool:
    """Makes the downloaded photo the image, once it is there (an empty download is a failure: kept as is)"""
    if not state.downloaded:
        return False
    data, state.downloaded = state.downloaded, None
    decoded = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
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
        This example shows a example of image processing (sobel filter) where you can adjust the params and see their effect in real time.

        * Pan and zoom the image with the mouse and the mouse wheel
        * Apply Colormaps to the filtered image in the options tab.
        """
    )
    imgui.separator()

    changed = gui_sobel_params(static.app_state.sobel_params)
    imgui.same_line(spacing=immapp.em_size(3))
    if imgui.button("Random photo"):
        download_random_photo(static.app_state)
    new_image = take_downloaded_photo(static.app_state)
    if changed or new_image:
        static.app_state.image_sobel = compute_sobel(
            static.app_state.image, static.app_state.sobel_params
        )
    static.app_state.immvision_params.refresh_image = new_image
    static.app_state.immvision_params_sobel.refresh_image = changed or new_image

    immvision.image(
        "Original", static.app_state.image, static.app_state.immvision_params
    )
    imgui.same_line()
    immvision.image(
        "Deriv", static.app_state.image_sobel, static.app_state.immvision_params_sobel
    )


def main():
    immapp.run_with_markdown(gui, window_size=(1000, 1000))


# The main entry point will run our GUI function
if __name__ == "__main__":
    main()
