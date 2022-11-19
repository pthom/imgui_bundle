from __future__ import annotations
from typing import List

import os.path
import cv2
import numpy as np

from imgui_bundle import imgui as imgui
from imgui_bundle import imgui_node_editor as imgui_node_editor, immvision as immvision, run
from imgui_bundle.demos.node_fn_compose.node_fn_compose import *


Image = np.ndarray


class MainImageViewer:
    class ImageAndParams:
        image: Image
        image_params: immvision.ImageParams

        def __init__(self):
            self.image_params = immvision.ImageParams()

    image_and_params: List[ImageAndParams]

    def __init__(self):
        self.image_and_params = []
        self.image = np.zeros((200, 200,  3), np.int8)
        self.image_params = immvision.ImageParams()
        self.image_params.image_display_size = (400, 400)
        self.image_params.refresh_image = True

    def set_image(self, image):
        self.image = image

    def gui(self):
        immvision.image("Image Debug", self.image, self.image_params)


IMAGE_VIEWER = MainImageViewer()


class ImageWithGui(AnyDataWithGui):
    image: Image

    def __init__(self, image: Image):
        self.image = image

    def gui_data(self, draw_thumbnail: bool = False) -> None:
        # imgui.push_id(str(id(self)))
        id_add = str(id(self))
        immvision.image_display(
            "Image##" + id_add,
            self.image,
            image_display_size=(100, 0),
            refresh_image=True
        )
        if imgui.is_item_clicked(0):
            IMAGE_VIEWER.set_image(self.image)
        # imgui.pop_id()


class GaussianBlurWithGui(FunctionWithGui):
    sigma_x: float = 3.
    sigma_y: float = 3.

    def f(self, x: ImageWithGui) -> ImageWithGui:
        ksize = (0, 0)
        blur = cv2.GaussianBlur(x.image, ksize=ksize, sigmaX=self.sigma_x, sigmaY=self.sigma_y)
        return ImageWithGui(blur)

    def name(self):
        return "GaussianBlur"

    def gui_params(self) -> bool:
        imgui.set_next_item_width(100)
        changed1, self.sigma_x = imgui.slider_float("sigma_x", self.sigma_x, 0.1, 15.)
        imgui.set_next_item_width(100)
        changed2, self.sigma_y = imgui.slider_float("sigma_y", self.sigma_y, 0.1, 15.)
        return changed1 or changed2


class CannyWithGui(FunctionWithGui):
    t_lower = 100  # Lower Threshold
    t_upper = 200  # Upper threshold
    aperture_size = 5  # Aperture size (3, 5, or 7)

    def f(self, x: ImageWithGui) -> ImageWithGui:
        edge = cv2.Canny(x.image, self.t_lower, self.t_upper, apertureSize=self.aperture_size)
        return ImageWithGui(edge)

    def name(self):
        return "Canny"

    def gui_params(self) -> bool:
        imgui.set_next_item_width(100)
        changed1, self.t_lower = imgui.slider_int("t_lower", self.t_lower, 0, 255)
        imgui.set_next_item_width(100)
        changed2, self.t_upper = imgui.slider_int("t_upper", self.t_upper, 0, 255)
        imgui.set_next_item_width(100)

        imgui.text("Aperture")
        imgui.same_line()
        changed3 = False
        for aperture_value in [3, 5, 7]:
            clicked, self.aperture_size = imgui.radio_button(str(aperture_value), self.aperture_size, aperture_value)
            if clicked:
                changed3 = True
            imgui.same_line()
        imgui.new_line()
        return changed1 or changed2 or changed3


def main():
    this_dir = os.path.dirname(__file__)
    resource_dir = this_dir + "/../immvision/resources"

    image = cv2.imread(resource_dir + "/house.jpg")

    functions = [GaussianBlurWithGui(), CannyWithGui()]
    nodes = FunctionCompositionNodes(functions)

    x = ImageWithGui(image)
    nodes.set_input(x)

    def gui():
        imgui.text(f"FPS: {imgui.get_io().framerate}")
        IMAGE_VIEWER.gui()
        ed.begin("AAA")
        nodes.draw()
        ed.end()

    config_node = imgui_node_editor.Config()
    config_node.settings_file = "demo_compose_image_debug.json"
    run(gui, with_node_editor_config=config_node, window_size=(1200, 1000), window_title="Functions composition")


if __name__ == "__main__":
    main()
