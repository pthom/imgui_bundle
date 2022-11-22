from imgui_bundle.demos.demo_composition_graph.functions_composition_graph import AnyDataWithGui, FunctionWithGui
from imgui_bundle import immvision, imgui

import numpy as np
from typing import List, Union


Image = np.ndarray


def split_channels(image: Image) -> Image:
    assert len(image.shape) == 3
    depth_first = np.squeeze(np.dsplit(image,image.shape[-1]))
    return depth_first


class ImageWithGui(AnyDataWithGui):
    array: Image
    image_params: immvision.ImageParams

    def __init__(self, image: Image, zoom_key="z", image_display_width=200):
        self.array = image
        self.first_frame = True
        self.image_params = immvision.ImageParams()
        self.image_params.image_display_size = (image_display_width, 0)
        self.image_params.zoom_key = zoom_key

    def gui_data(self, function_name: str) -> None:
        self.image_params.refresh_image = self.first_frame
        immvision.image(function_name, self.array, self.image_params)
        self.first_frame = False
        if imgui.small_button("Inspect"):
            immvision.inspector_add_image(self.array, function_name)


class ImagesWithGui(AnyDataWithGui):
    array: Image
    images_params: List[immvision.ImageParams]

    def __init__(self,
                 images: Image, # images is a numpy of several image along the first axis
                 zoom_key="z",
                 image_display_width=200,
                 share_image_params: bool = False
                 ):
        self.array = images
        self.first_frame = True

        def make_image_params():
            image_params = immvision.ImageParams()
            image_params.image_display_size = (image_display_width, 0)
            image_params.zoom_key = zoom_key
            return image_params

        self.images_params = []
        if share_image_params:
            self.images_params.append(make_image_params())
        else:
            for i in range(len(images)):
                self.images_params.append(make_image_params())

    def gui_data(self, function_name: str) -> None:
        refresh_image = self.first_frame
        self.first_frame = False

        for i, image in enumerate(self.array):
            image_params = self.images_params[i] if i < len(self.images_params) else self.images_params[0]
            image_params.refresh_image = refresh_image
            label = f"{function_name} - {i}"
            immvision.image(label, image, image_params)
            if imgui.small_button("Inspect"):
                immvision.inspector_add_image(image, label)


class AdjustImage:
    pow_value: float = 1

    def apply(self, image: Image) -> Image:
        image_adjusted = np.power(image, self.pow_value)
        return image_adjusted

    def gui_params(self) -> bool:
        imgui.set_next_item_width(100)
        changed, self.pow_value = imgui.slider_float("power", self.pow_value, 0., 10.)
        return changed


class SplitChannelsWithGui(FunctionWithGui):
    def f(self, x: AnyDataWithGui) -> ImagesWithGui:
        assert type(x) == ImageWithGui
        channels = split_channels(x.array)
        channels_normalized = channels / 255.
        r = ImagesWithGui(channels_normalized)
        return r

    def name(self) -> str:
        return "SplitChannels"


class AdjustImageWithGui(FunctionWithGui):
    adjust_image: AdjustImage

    def __init__(self):
        self.adjust_image = AdjustImage()

    def f(self, x: AnyDataWithGui) -> ImageWithGui:
        assert type(x) == ImageWithGui

        image_adjusted = self.adjust_image.apply(x.array)
        return ImageWithGui(image_adjusted)

    def name(self) -> str:
        return "AdjustImage"

    def gui_params(self) -> bool:
        return self.adjust_image.gui_params()


class AdjustChannelsWithGui(FunctionWithGui):
    channel_adjust_params: List[AdjustImage]

    def __init__(self):
        self.channel_adjust_params = []

    def add_params_on_demand(self, nb_channels: int):
        while len(self.channel_adjust_params) < nb_channels:
            self.channel_adjust_params.append(AdjustImage())

    def f(self, x: AnyDataWithGui) -> ImagesWithGui:
        assert type(x) == ImagesWithGui
        channels = x.array

        self.add_params_on_demand(len(channels))

        for i in range(len(channels)):
            channels[i] = self.channel_adjust_params[i].apply(channels[i])

        r = ImagesWithGui(channels)
        return r

    def name(self) -> str:
        return "ProcessChannels"

    def gui_params(self) -> bool:
        changed = False
        for i, channel_adjust_param in enumerate(self.channel_adjust_params):
            imgui.push_id(i)
            changed |= channel_adjust_param.gui_params()
            imgui.pop_id()
        return changed


class MergeChannelsWithGui(FunctionWithGui):
    def f(self, x: AnyDataWithGui) -> ImageWithGui:
        assert type(x) == ImagesWithGui
        channels = [c for c in x.array]
        image_float = np.dstack(channels)
        image_int = (image_float * 255.).astype("uint8")
        r = ImageWithGui(image_int)
        return r

    def name(self) -> str:
        return "MergeChannels"

