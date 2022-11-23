from __future__ import annotations
from typing import List

import os.path
import cv2
import numpy as np

from imgui_bundle import imgui, hello_imgui
from imgui_bundle import imgui_node_editor as imgui_node_editor
from imgui_bundle.demos.demo_composition_graph.functions_composition_graph import *
from imgui_bundle.demos.demo_composition_graph.functions_composition_graph.image_with_gui import *


class GaussianBlurWithGui(FunctionWithGui):
    sigma_x: float = 3.0
    sigma_y: float = 3.0

    def f(self, x: AnyDataWithGui) -> ImageWithGui:
        assert type(x) == ImageWithGui
        ksize = (0, 0)
        blur = cv2.GaussianBlur(x.array, ksize=ksize, sigmaX=self.sigma_x, sigmaY=self.sigma_y)
        return ImageWithGui(blur)

    def name(self):
        return "GaussianBlur"

    def gui_params(self) -> bool:
        imgui.set_next_item_width(100)
        changed1, self.sigma_x = imgui.slider_float("sigma_x", self.sigma_x, 0.1, 15.0)
        imgui.set_next_item_width(100)
        changed2, self.sigma_y = imgui.slider_float("sigma_y", self.sigma_y, 0.1, 15.0)
        return changed1 or changed2


class CannyWithGui(FunctionWithGui):
    t_lower = 100  # Lower Threshold
    t_upper = 200  # Upper threshold
    aperture_size = 5  # Aperture size (3, 5, or 7)

    def f(self, x: AnyDataWithGui) -> ImageWithGui:
        assert type(x) == ImageWithGui
        edge = cv2.Canny(x.array, self.t_lower, self.t_upper, apertureSize=self.aperture_size)
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
            clicked: bool
            clicked, self.aperture_size = imgui.radio_button(str(aperture_value), self.aperture_size, aperture_value)  # type: ignore
            if clicked:
                changed3 = True
            imgui.same_line()
        imgui.new_line()
        return changed1 or changed2 or changed3


def main():
    this_dir = os.path.dirname(__file__)
    resource_dir = this_dir + "/../immvision/resources"
    image = cv2.imread(resource_dir + "/tennis.jpg")
    image = cv2.resize(image, (int(image.shape[1] * 0.3), int(image.shape[0] * 0.3)))

    x = ImageWithGui(image)

    # functions = [GaussianBlurWithGui(), CannyWithGui()]
    functions = [SplitChannelsWithGui(), LutChannelsWithGui(), MergeChannelsWithGui()]

    composition_graph = FunctionsCompositionGraph(functions)
    composition_graph.set_input(x)

    def gui():
        # runner_params = hello_imgui.get_runner_params()
        # runner_params.imgui_window_params.default_imgui_window_type = hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
        # runner_params.imgui_window_params.enable_viewports = True

        # imgui.begin("graph")
        imgui.text(f"FPS: {imgui.get_io().framerate}")
        composition_graph.draw()
        # imgui.end()

        # imgui.begin("Inspector")
        # immvision.inspector_show()
        # imgui.end()

    config_node = imgui_node_editor.Config()
    config_node.settings_file = "demo_compose_image_debug.json"

    import imgui_bundle

    imgui_bundle.run(
        gui,
        with_node_editor_config=config_node,
        with_implot=True,
        window_size=(1200, 1000))


if __name__ == "__main__":
    main()
