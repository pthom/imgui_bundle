from __future__ import annotations

import os.path

from imgui_bundle.demos.api_demos import *
from imgui_bundle.demos.demo_composition_graph.functions_composition_graph import *
from imgui_bundle.demos.demo_composition_graph.functions_composition_graph.image_with_gui import *

import imgui_bundle


class GaussianBlurWithGui(FunctionWithGui):
    sigma_x: float = 3.0
    sigma_y: float = 3.0

    def __init__(self):
        self.input_gui = ImageWithGui()
        self.output_gui = ImageWithGui()

    def f(self, x: Any) -> Image:
        assert type(x) == Image
        ksize = (0, 0)
        blur = cv2.GaussianBlur(x, ksize=ksize, sigmaX=self.sigma_x, sigmaY=self.sigma_y)
        return blur

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

    def __init__(self):
        self.input_gui = ImageWithGui()
        self.output_gui = ImageWithGui()

    def f(self, x: Any) -> Image:
        assert type(x) == Image
        edge = cv2.Canny(x, self.t_lower, self.t_upper, apertureSize=self.aperture_size)
        return edge

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


class OilPaintingWithGui(FunctionWithGui):
    dynRatio = 1  # image is divided by dynRatio before histogram processing
    size = 3  # size	neighbouring size is 2-size+1
    color_conversion: CvColorConversionCode  # color space conversion code

    def __init__(self):
        self.input_gui = ImageWithGui()
        self.output_gui = ImageWithGui()
        self.color_conversion = cv2.COLOR_BGR2HSV

    def f(self, x: Any) -> Image:
        assert type(x) == Image
        r = np.zeros_like(x)
        # pip install opencv-contrib-python
        r = cv2.xphoto.oilPainting(x, self.size, self.dynRatio, self.color_conversion)
        return r

    def name(self):
        return "Oil Painting"

    def gui_params(self) -> bool:
        imgui.set_next_item_width(100)
        changed1, self.dynRatio = imgui.slider_int("dynRatio", self.dynRatio, 1, 10)
        imgui.set_next_item_width(100)
        changed2, self.size = imgui.slider_int("size", self.size, 1, 10)
        return changed1 or changed2


def main():
    this_dir = os.path.dirname(__file__)
    image = cv2.imread(demos_assets_folder() + "/images/house.jpg")
    image = cv2.resize(image, (int(image.shape[1] * 0.5), int(image.shape[0] * 0.5)))

    split_lut_merge_gui = Split_Lut_Merge_WithGui(ColorType.BGR)

    functions = [split_lut_merge_gui.split, split_lut_merge_gui.lut, split_lut_merge_gui.merge, OilPaintingWithGui()]
    # functions = [GaussianBlurWithGui(), CannyWithGui()]

    composition_graph = FunctionsCompositionGraph(functions)
    composition_graph.set_input(image)

    def gui():
        from imgui_bundle import hello_imgui

        hello_imgui.get_runner_params().fps_idle = 0
        imgui.text(f"FPS: {imgui.get_io().framerate}")
        composition_graph.draw()

    config_node = imgui_node_editor.Config()
    config_node.settings_file = "demo_compose_image.json"
    imgui_bundle.run(gui, with_node_editor_config=config_node, window_size=(1600, 1000), fps_idle=0)

    # functions = [GaussianBlurWithGui(), CannyWithGui()]
    # functions = [GaussianBlurWithGui(), CannyWithGui()]
    # functions = [SplitChannelsWithGui(), LutChannelsWithGui(), MergeChannelsWithGui()]
    # functions = [SplitChannelsWithGui(), LutChannelsWithGui(), MergeChannelsWithGui()]


if __name__ == "__main__":
    main()
