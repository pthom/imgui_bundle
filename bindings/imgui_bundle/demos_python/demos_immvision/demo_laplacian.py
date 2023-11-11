# Adaptation of https://docs.opencv.org/4.x/df/d0d/tutorial_find_contours.html

from imgui_bundle import imgui, immapp, immvision
from imgui_bundle.demos_python import demo_utils
import cv2  # type: ignore
import numpy as np
from numpy.typing import NDArray


# First, lets define `LaplacianData` (a class that contains an image and its laplacian)
class LaplacianData:
    src_gray: NDArray[np.float64]
    laplacian: NDArray[np.float64]

    blur_half_size: int = 1
    kernel_half_size: int = 1

    params: immvision.ImageParams

    def __init__(self, image_file: str):
        img = cv2.imread(image_file)
        img = cv2.resize(img, dsize=None, fx=0.5, fy=0.5)  # type: ignore
        gray_uint8 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.src_gray = gray_uint8 / 255.0
        self.update_laplacian()

        self.params = immvision.ImageParams()
        self.params.image_display_size = (400, 0)
        self.params.show_options_panel = True

    def update_laplacian(self):
        ddepth = cv2.CV_64F
        blur_width = self.blur_half_size * 2 + 1
        kernel_size = self.kernel_half_size * 2 + 1
        blur = cv2.GaussianBlur(self.src_gray, (blur_width, blur_width), 0)
        self.laplacian = cv2.Laplacian(blur, ddepth, ksize=kernel_size)


# Then let's define `gui_laplacian` (a gui that display and manipulates LaplacianData)
def gui_laplacian(data: LaplacianData):
    changed1, data.blur_half_size = imgui.slider_int(
        "Blur half size", data.blur_half_size, 1, 10
    )
    changed2, data.kernel_half_size = imgui.slider_int(
        "Kernel half size", data.kernel_half_size, 1, 10
    )
    changed = changed1 or changed2
    if changed:
        data.update_laplacian()
    data.params.refresh_image = changed
    immvision.image("Laplacian", data.laplacian, data.params)


# Then, let's instantiate our LaplacianData
laplacian_data = LaplacianData(demo_utils.demos_assets_folder() + "/images/house.jpg")


# Finally, define a parameterless gui function from it
def my_gui_laplacian():
    gui_laplacian(laplacian_data)


def main():
    immapp.run_nb(my_gui_laplacian)


if __name__ == "__main__":
    main()
