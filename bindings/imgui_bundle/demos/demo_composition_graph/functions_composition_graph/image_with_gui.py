from imgui_bundle.demos.demo_composition_graph.functions_composition_graph import AnyDataWithGui
from imgui_bundle import immvision, imgui

import numpy as np


Image = np.ndarray


class ImageWithGui(AnyDataWithGui):
    image: Image
    image_params: immvision.ImageParams
    name: str

    def __init__(self, image: Image):
        self.image = image
        self.first_frame = True
        self.image_params = immvision.ImageParams()
        self.image_params.image_display_size = (250, 0)
        self.image_params.zoom_key = "z"

    def gui_data(self, function_name: str) -> None:
        self.image_params.refresh_image = self.first_frame
        immvision.image(function_name, self.image, self.image_params)
        self.first_frame = False
        if imgui.small_button("Inspect"):
            immvision.inspector_add_image(self.image, "Image")


