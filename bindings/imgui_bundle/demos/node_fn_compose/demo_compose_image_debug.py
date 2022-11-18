from __future__ import annotations

import os.path
import cv2
import numpy as np
from imgui_bundle import imgui_node_editor as imgui_node_editor, immvision as immvision
from imgui_bundle.demos.node_fn_compose.node_fn_compose import *


Image = np.ndarray


class ImageWithGui(AnyDataWithGui):
    image: Image

    def __init__(self, image: Image):
        self.image = image

    def gui_data(self, draw_thumbnail: bool = False) -> None:
        imgui.push_id(str(id(self)))
        immvision.image_display("Image", self.image, image_display_size=(100, 0))
        imgui.pop_id()


class CannyWithGui(FunctionWithGui):
    t_lower = 100  # Lower Threshold
    t_upper = 200  # Upper threshold
    aperture_size = 5  # Aperture size

    def __init__(self):
        self.what_to_add = 1

    def f(self, x: ImageWithGui) -> ImageWithGui:
        edge = cv2.Canny(x.image, self.t_lower, self.t_upper,
                         apertureSize=self.aperture_size)
        return ImageWithGui(edge)

    def name(self):
        return "CannyWithGui"

    def gui_params(self) -> bool:
        imgui.set_next_item_width(100)
        changed1, self.t_lower = imgui.slider_int("t_lower", self.t_lower, 0, 255)
        imgui.set_next_item_width(100)
        changed2, self.t_upper = imgui.slider_int("t_upper", self.t_upper, 0, 255)
        imgui.set_next_item_width(100)
        changed3, self.aperture_size = imgui.slider_int("aperture_size", self.aperture_size, 0, 20)
        return changed1 or changed2 or changed3


def main():
    this_dir = os.path.dirname(__file__)
    resource_dir = this_dir + "/../immvision/resources"

    image = cv2.imread(resource_dir + "/house.jpg")
    image_params = immvision.ImageParams()
    image_params.image_display_size = (400, 400)
    image_params.zoom_key = "z"

    image_params_sobel = immvision.ImageParams()
    image_params_sobel.zoom_key = image_params.zoom_key
    image_params_sobel.image_display_size = image_params.image_display_size
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_gray = image_gray / 255.
    sobel_x = cv2.Sobel(image_gray, cv2.CV_64F, 1, 0, ksize=5)
    # immvision.debug("sobel", sobel_x)

    debug_image = image

    functions = [CannyWithGui()]
    nodes = FunctionCompositionNodes(functions)

    x = ImageWithGui(image)
    nodes.set_input(x)

    def gui():
        nonlocal x

        immvision.image("Image Debug", debug_image, image_params)
        imgui.same_line()
        immvision.image("Image Gray", sobel_x, image_params_sobel)

        # _, x.value = imgui.slider_int("X", x.value, 0, 10)
        # if imgui.button("Apply"):
        #     nodes.set_input(x)

        ed.begin("AAA")
        nodes.draw()
        ed.end()

    config_node = imgui_node_editor.Config()
    config_node.settings_file = "demo_compose_image_debug.json"
    run(gui, with_node_editor_config=config_node, window_size=(1200, 1000), window_title="Functions composition")


if __name__ == "__main__":
    main()
