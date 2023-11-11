# Adaptation of https://docs.opencv.org/4.x/df/d0d/tutorial_find_contours.html

from imgui_bundle import imgui, immapp, immvision
from imgui_bundle.demos_python import demo_utils
import cv2  # type: ignore
import random as rng
import numpy as np
from numpy.typing import NDArray


class BlurData:
    src_gray: NDArray[np.uint8]
    contours: NDArray[np.uint8]
    thresh: int = 100

    def __init__(self, image_file: str):
        img = cv2.imread(image_file)
        img = cv2.resize(img, dsize=None, fx=0.5, fy=0.5)  # type: ignore
        self.src_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.update_contours()

    def update_contours(self):
        canny_output = cv2.Canny(self.src_gray, self.thresh, self.thresh * 2)
        contours, hierarchy = cv2.findContours(
            canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        self.contours = np.zeros(
            (canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8
        )
        for i in range(len(contours)):
            color = (rng.randint(0, 256), rng.randint(0, 256), rng.randint(0, 256))
            cv2.drawContours(
                self.contours, contours, i, color, 2, cv2.LINE_8, hierarchy, 0
            )


def gui_blur(blur_data: BlurData):
    min_thresh = 20
    max_thresh = 500
    image_display_size = (400, 0)
    changed, blur_data.thresh = imgui.slider_int(
        "Canny thresh", blur_data.thresh, min_thresh, max_thresh
    )
    if changed:
        blur_data.update_contours()
    immvision.image_display("img", blur_data.src_gray, image_display_size)
    imgui.same_line()
    immvision.image_display("contours", blur_data.contours, image_display_size, changed)


def main():
    blur_data = BlurData(demo_utils.demos_assets_folder() + "/images/house.jpg")

    def gui():
        gui_blur(blur_data)

    immapp.run(gui, "blur", True)


if __name__ == "__main__":
    main()
