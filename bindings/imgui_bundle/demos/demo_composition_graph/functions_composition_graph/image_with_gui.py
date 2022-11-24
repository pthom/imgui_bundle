from __future__ import annotations
from typing import Any, Dict, Callable

import imgui_bundle
from imgui_bundle.demos.demo_composition_graph.functions_composition_graph import AnyDataWithGui, FunctionWithGui
from imgui_bundle.demos.demo_composition_graph.functions_composition_graph.cv_color_type import *
from imgui_bundle import immvision, imgui, ImVec2
from imgui_bundle import imgui_node_editor

import numpy as np
import math
from typing import List, Tuple, Optional, cast
import cv2


Image = np.ndarray


def split_channels(image: Image) -> Image:
    assert len(image.shape) == 3
    depth_first = np.squeeze(np.dsplit(image, image.shape[-1]))
    return depth_first


class ImageWithGui(AnyDataWithGui):
    array: Optional[Image]
    image_params: immvision.ImageParams

    def __init__(self, image: Optional[Image] = None, zoom_key="z", image_display_width=200):
        self.array = image
        self.first_frame = True
        self.image_params = immvision.ImageParams()
        self.image_params.image_display_size = (image_display_width, 0)
        self.image_params.zoom_key = zoom_key

    def get(self) -> Optional[Any]:
        return self.array

    def set(self, v: Any) -> None:
        assert type(v) == Image
        self.array = v
        self.first_frame = True

    def gui_data(self, function_name: str) -> None:
        self.image_params.refresh_image = self.first_frame
        _, self.image_params.image_display_size = gui_edit_size(self.image_params.image_display_size)
        if self.array is not None:
            immvision.image(function_name, self.array, self.image_params)
            self.first_frame = False
        if imgui.small_button("Inspect"):
            immvision.inspector_add_image(self.array, function_name)

    def gui_set_input(self) -> Optional[Any]:
        from imgui_bundle import im_file_dialog as ifd

        if imgui.button("Select image file"):
            ifd.FileDialog.instance().open(
                "ImageOpenDialog",
                "Choose an image",
                "Image file (*.png*.jpg*.jpeg*.bmp*.tga).png,.jpg,.jpeg,.bmp,.tga,.*",
                False,
            )

        result = None
        imgui_node_editor.suspend_editor_canvas()
        if ifd.FileDialog.instance().is_done("ImageOpenDialog"):
            if ifd.FileDialog.instance().has_result():
                ifd_result = ifd.FileDialog.instance().get_result().path()
                image = cv2.imread(ifd_result)
                if image is not None:
                    result = image
            ifd.FileDialog.instance().close()
        imgui_node_editor.resume_editor_canvas()

        return result


class ImageChannelsWithGui(AnyDataWithGui):
    array: Optional[Image]  # We are displaying the different channels of this image
    images_params: immvision.ImageParams
    color_type: ColorType = ColorType.BGR

    def __init__(
        self,
        images: Optional[Image] = None,  # images is a numpy of several image along the first axis
        zoom_key="z",
        image_display_width=200,
    ):
        self.array = images
        self.first_frame = True

        self.image_params = immvision.ImageParams()
        self.image_params.image_display_size = (image_display_width, 0)
        self.image_params.zoom_key = zoom_key

    def set(self, v: Any) -> None:
        assert type(v) == Image
        self.array = v
        self.first_frame = True

    def get(self) -> Optional[Any]:
        return self.array

    def gui_data(self, function_name: str) -> None:
        refresh_image = self.first_frame
        self.first_frame = False

        changed, self.image_params.image_display_size = gui_edit_size(self.image_params.image_display_size)
        if self.array is not None:
            for i, image in enumerate(self.array):
                channel_name = self.color_type.channel_name(i)
                self.image_params.refresh_image = refresh_image
                label = f"{channel_name}"
                immvision.image(label, image, self.image_params)
                if imgui.small_button("Inspect"):
                    immvision.inspector_add_image(image, label)


class SplitChannelsWithGui(FunctionWithGui):
    color_conversion: Optional[ColorConversion] = None
    gui_params_optional_fn: Callable[[], bool]

    def __init__(self):
        self.input_gui = ImageWithGui()
        self.output_gui = ImageChannelsWithGui()

    def output_gui_channels(self) -> ImageChannelsWithGui:
        return cast(ImageChannelsWithGui, self.output_gui)

    def f(self, x: Any) -> Any:
        assert type(x) == Image
        if self.color_conversion is not None:
            x_converted = cv2.cvtColor(x, self.color_conversion.conversion_code)
        else:
            x_converted = x
        channels = split_channels(x_converted)
        channels_normalized = channels / 255.0
        return channels_normalized

    def name(self) -> str:
        r = "Split Channels"
        if self.color_conversion is not None:
            r += " - " + self.color_conversion.name
        return r

    def gui_params(self) -> bool:
        if hasattr(self, "gui_params_optional_fn"):
            return self.gui_params_optional_fn()
        else:
            return False


class MergeChannelsWithGui(FunctionWithGui):
    color_conversion: Optional[ColorConversion] = None

    def __init__(self):
        self.input_gui = ImageChannelsWithGui()
        self.output_gui = ImageWithGui()

    def f(self, x: Any) -> Any:
        assert type(x) == Image
        channels = [c for c in x]
        image_float = np.dstack(channels)
        image_uint8 = (image_float * 255.0).astype("uint8")
        image_converted = image_uint8
        if self.color_conversion is not None:
            image_converted = cv2.cvtColor(image_uint8, self.color_conversion.conversion_code)
        return image_uint8

    def name(self) -> str:
        r = "Merge Channels"
        if self.color_conversion is not None:
            r += " - " + self.color_conversion.name
        return r


class Split_Lut_Merge_WithGui:
    possible_conversion_pairs: List[ColorConversionPair]
    current_conversion_pair: Optional[ColorConversionPair]
    show_possible_color_conversions: bool = False
    split: SplitChannelsWithGui
    lut: LutChannelsWithGui
    merge: MergeChannelsWithGui

    def __init__(self, color_type: ColorType):
        self.possible_conversion_pairs = compute_possible_conversion_pairs(color_type)
        self.current_conversion_pair = None
        self.split = SplitChannelsWithGui()
        self.split.gui_params_optional_fn = lambda: self.gui_select_conversion()
        self.merge = MergeChannelsWithGui()
        self.lut = LutChannelsWithGui()

    def gui_select_conversion(self) -> bool:
        changed = False
        _, self.show_possible_color_conversions = imgui.checkbox(
            "Show Color Conversions", self.show_possible_color_conversions
        )
        if self.show_possible_color_conversions:
            if imgui.radio_button("None", self.current_conversion_pair == None):
                changed = True
                self.current_conversion_pair = None
            for conversion_pair in self.possible_conversion_pairs:
                active = self.current_conversion_pair == conversion_pair
                if imgui.radio_button(conversion_pair.conversion.name, active):
                    self.current_conversion_pair = conversion_pair
                    changed = True

        if changed:
            if self.current_conversion_pair is None:
                self.split.color_conversion = None
                self.merge.color_conversion = None
                # self.lut.output_gui.color_type = ColorType.BGR
            else:
                self.split.color_conversion = self.current_conversion_pair.conversion
                self.merge.color_conversion = self.current_conversion_pair.inv_conversion

                self.lut.color_type = self.current_conversion_pair.conversion.dst_color
                self.lut.output_gui_channels().color_type = self.current_conversion_pair.conversion.dst_color
                self.split.output_gui_channels().color_type = self.current_conversion_pair.conversion.dst_color
                print("a")
        return changed


CvSize = Tuple[int, int]


def gui_edit_size(size: CvSize) -> Tuple[bool, CvSize]:
    def modify_size_by_ratio(ratio: float) -> CvSize:
        w = int(size[0] * ratio + 0.5)
        h = int(size[1] * ratio + 0.5)
        return w, h

    changed = False
    ratio = 1.05
    imgui.push_button_repeat(True)
    imgui.text("Thumbnail size")
    imgui.same_line()
    if imgui.small_button(" smaller "):
        size = modify_size_by_ratio(1.0 / ratio)
        changed = True
    imgui.same_line()
    if imgui.small_button(" bigger "):
        size = modify_size_by_ratio(ratio)
        changed = True
    imgui.pop_button_repeat()

    return changed, size


###############################################################################
#     LUT
###############################################################################

Point2d = Tuple[float, float]


class LutImage:
    pow_exponent: float = 1.0
    min_in: float = 0.0
    min_out: float = 0.0
    max_in: float = 1.0
    max_out: float = 1.0

    _lut_table: np.ndarray
    _lut_graph: np.ndarray
    _lut_graph_needs_refresh: bool = True

    def apply(self, image: Image) -> Image:
        if not hasattr(self, "_lut_table"):
            self._prepare_lut()
        lut_uint8 = (self._lut_table * 255.0).astype(np.uint8)
        image_uint8 = (image * 255.0).astype(np.uint8)
        image_with_lut_uint8 = np.zeros_like(image_uint8)
        cv2.LUT(image_uint8, lut_uint8, image_with_lut_uint8)
        image_adjusted = image_with_lut_uint8 / 255.0
        return image_adjusted

    @staticmethod
    def _lut_graph_size() -> float:
        graph_size = int(imgui_bundle.em_size() * 2.0)
        return graph_size

    def _show_lut_graph(self, channel_name: str) -> Point2d:
        if not hasattr(self, "_lut_graph"):
            self._prepare_lut_graph()
        mouse_position = immvision.image_display(
            channel_name, self._lut_graph, refresh_image=self._lut_graph_needs_refresh
        )
        self._lut_graph_needs_refresh = False
        return mouse_position

    def _prepare_lut_graph(self):
        graph_size = self._lut_graph_size()
        x = np.arange(0.0, 1.0, 1.0 / 256.0)
        self._lut_graph = immvision._draw_lut_graph(list(x), list(self._lut_table), (graph_size, graph_size))  # type: ignore
        self._lut_graph_needs_refresh = True

    def _prepare_lut(self):
        x = np.arange(0.0, 1.0, 1.0 / 256.0)
        y = (x - self.min_in) / (self.max_in - self.min_in)
        y = np.clip(y, 0.0, 1.0)
        y = np.power(y, self.pow_exponent)
        y = np.clip(y, 0.0, 1.0)
        y = self.min_out + (self.max_out - self.min_out) * y
        y = np.clip(y, 0.0, 1.0)
        self._lut_table = y

    def handle_graph_mouse_edit(self, mouse_position: Point2d) -> bool:
        drag_threshold = 0
        mouse_button = 0
        changed = False

        def get_mouse_position_normalized() -> Optional[Point2d]:
            r: Optional[Point2d] = None
            graph_size = self._lut_graph_size()
            if mouse_position[0] >= 0:
                r = (mouse_position[0] / graph_size, 1 - mouse_position[1] / graph_size)
                return r
            else:
                return None

        mouse_position_normalized = get_mouse_position_normalized()

        if mouse_position_normalized is not None:
            imgui.text(f"{mouse_position_normalized[0]:.2f}, {mouse_position_normalized[1]:.2f}")

        if mouse_position_normalized is not None and imgui.is_mouse_dragging(0, drag_threshold):
            drag_delta = imgui.get_mouse_drag_delta(mouse_button)
            drag_horizontal = math.fabs(drag_delta.x) > math.fabs(drag_delta.y)
            drag_vertical = not drag_horizontal
            imgui.reset_mouse_drag_delta(mouse_button)

            delta_edge = 0.37
            if drag_horizontal and mouse_position_normalized[1] < delta_edge:
                self.min_in = mouse_position_normalized[0]
                changed = True
            elif drag_horizontal and mouse_position_normalized[1] > 1.0 - delta_edge:
                self.max_in = mouse_position_normalized[0]
                changed = True
            elif drag_vertical and mouse_position_normalized[0] < delta_edge:
                self.min_out = mouse_position_normalized[1]
                changed = True
            elif drag_vertical and mouse_position_normalized[0] > 1.0 - delta_edge:
                self.max_out = mouse_position_normalized[1]
                changed = True

        return changed

    def gui_params(self, channel_name: str) -> bool:
        changed = False

        imgui.begin_group()
        mouse_position = self._show_lut_graph(channel_name)
        if self.handle_graph_mouse_edit(mouse_position):
            changed = True

        if imgui.small_button("Reset"):
            self.min_in, self.max_in = (0.0, 1.0)
            self.min_out, self.max_out = (0.0, 1.0)
            self.pow_exponent = 1.0
            changed = True
        imgui.end_group()

        imgui.same_line()

        imgui.begin_group()
        idx_slider = 0

        def show_slider(label: str, v: float, min: float, max: float, logarithmic: bool) -> float:
            nonlocal idx_slider, changed
            imgui.set_next_item_width(70)
            idx_slider += 1
            flags = imgui.ImGuiSliderFlags_.logarithmic if logarithmic else 0
            edited_this_slider, v = imgui.slider_float(
                f"{label}##slider{idx_slider}", v, min, max, flags=flags
            )  # type: ignore
            if edited_this_slider:
                changed = True
            return v

        def show_01_slider(label: str, v: float) -> float:
            return show_slider(label, v, 0, 1, False)

        def show_two_01_sliders(label: str, v_min: float, v_max) -> Tuple[float, float]:
            v_min = show_01_slider(f"##{label}v_min", v_min)
            imgui.same_line()
            v_max = show_01_slider(f"{label}##v_max", v_max)
            if math.fabs(v_max - v_min) < 1e-3:  # avoid div by 0
                v_min = v_max - 0.01
            return v_min, v_max

        self.pow_exponent = show_slider("Gamma power", self.pow_exponent, 0.0, 10.0, True)
        self.min_in, self.max_in = show_two_01_sliders("In", self.min_in, self.max_in)
        self.min_out, self.max_out = show_two_01_sliders("Out", self.min_out, self.max_out)

        if changed:
            self._prepare_lut()
            self._prepare_lut_graph()
        imgui.end_group()
        return changed


class LutImageWithGui(FunctionWithGui):
    lut_image: LutImage

    def __init__(self):
        self.lut_image = LutImage()
        self.input_gui = ImageWithGui()
        self.output_gui = ImageWithGui()

    def f(self, x: Any) -> Any:
        assert type(x) == Image
        image_adjusted = self.lut_image.apply(x)
        return image_adjusted

    def name(self) -> str:
        return "LUT"

    def gui_params(self) -> bool:
        return self.lut_image.gui_params("LUT")


class LutChannelsWithGui(FunctionWithGui):
    color_type: ColorType = ColorType.BGR
    channel_adjust_params: List[LutImage]

    def __init__(self):
        self.input_gui = ImageChannelsWithGui()
        self.output_gui = ImageChannelsWithGui()

    def output_gui_channels(self) -> ImageChannelsWithGui:
        return cast(ImageChannelsWithGui, self.output_gui)

    def add_params_on_demand(self, nb_channels: int):
        if not hasattr(self, "channel_adjust_params"):
            self.channel_adjust_params = []
        while len(self.channel_adjust_params) < nb_channels:
            self.channel_adjust_params.append(LutImage())

    def f(self, x: Any) -> Any:
        assert type(x) == Image

        original_channels = x
        self.add_params_on_demand(len(original_channels))

        adjusted_channels = np.zeros_like(original_channels)
        for i in range(len(original_channels)):
            adjusted_channels[i] = self.channel_adjust_params[i].apply(original_channels[i])

        return adjusted_channels

    def name(self) -> str:
        return "LUT channels"

    def gui_params(self) -> bool:
        changed = False
        for i, channel_adjust_param in enumerate(self.channel_adjust_params):
            channel_name = self.color_type.channels_names()[i]
            imgui.push_id(str(i))
            changed |= channel_adjust_param.gui_params(channel_name)
            imgui.pop_id()
        return changed
