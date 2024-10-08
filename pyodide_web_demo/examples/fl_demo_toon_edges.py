import time

import fiatlight as fl
from fiatlight.fiat_types import PositiveFloat, ColorRgb
from fiatlight.fiat_kits.fiat_image import ImageU8_GRAY, ImageRgb
from fiatlight.demos.images.opencv_wrappers import canny, dilate, MorphShape, CannyApertureSize
from fiatlight.fiat_kits.fiat_image import overlay_alpha_image
from pydantic import BaseModel
import numpy as np
import cv2


def image_from_url(url: str = "") -> ImageRgb:
    from imgui_bundle.demos_python import demo_utils
    img = fl.imread_rgb(demo_utils.demos_assets_folder() + "/images/house.jpg")
    return img


@fl.with_fiat_attributes(edges_intensity__range=(0.0, 1.0))
def merge_toon_edges(
        image: ImageRgb,
        edges_images: ImageU8_GRAY,
        edges_intensity: float = 0.7,
        edges_color: ColorRgb = ColorRgb((0, 0, 0)),
        is_image_bgr: bool = True,
) -> ImageRgb:
    """Add toon edges to the image.
    :param image: Image: Input image
    :param edges_images: binary image with edges detected using Canny filter
    :param blur_sigma: Optional sigma value for Gaussian Blur applied to edges (skip if 0)
    :param edges_intensity: Intensity of the edges
    :param edges_color: Color of the edges
    """
    if is_image_bgr:
        edges_color = ColorRgb((edges_color[2], edges_color[1], edges_color[0]))

    # Create an RGBA image that will be overlaid on the original image
    # Its color will be constant (color) and its alpha channel will be the edges_images
    overlay_rgba = np.zeros((*image.shape[:2], 4), dtype=np.uint8)
    overlay_rgba[:, :, :3] = edges_color
    overlay_rgba[:, :, 3] = (edges_images * edges_intensity).astype(np.uint8)

    # Overlay the RGBA image on the original image
    r = overlay_alpha_image(image, overlay_rgba)  # type: ignore

    return r


@fl.base_model_with_gui_registration(
    blur_sigma__range=(0.0, 10.0),
)
class ToonCannyParams(BaseModel):
    t_lower: PositiveFloat = PositiveFloat(1000.0)
    t_upper: PositiveFloat = PositiveFloat(5000.0)
    l2_gradient: bool = True
    blur_sigma: float = 0.0
    aperture_size: CannyApertureSize = CannyApertureSize.APERTURE_5


@fl.base_model_with_gui_registration(
    kernel_size__range=(0, 10),
    iterations__range=(0, 10),
)
class ToonDilateParams(BaseModel):
    kernel_size: int = 2
    morph_shape: MorphShape = MorphShape.MORPH_ELLIPSE
    iterations: int = 2


@fl.base_model_with_gui_registration(
    blur_sigma__range=(0.0, 10.0),
    intensity__range=(0.0, 1.0),
)
class ToonEdgesAppearance(BaseModel):
    blur_sigma: float = 0.0
    intensity: float = 0.8
    color: ColorRgb = ColorRgb((0, 0, 0))


@fl.base_model_with_gui_registration(
    canny__tooltip="Params for the edge detection",
    dilate__tooltip="Params for the edge dilation (make it thicker)",
    appearance__tooltip="Params for the appearance of the edges",
)
class ToonEdgesParams(BaseModel):
    canny: ToonCannyParams = ToonCannyParams()
    dilate: ToonDilateParams = ToonDilateParams()
    appearance: ToonEdgesAppearance = ToonEdgesAppearance()


@fl.with_fiat_attributes(
    params__tooltip="Parameters for the Toon Edges function",
    params__label="Edges Params",
    label="Add Toon Edges",
)
def add_toon_edges(image: ImageRgb, params: ToonEdgesParams) -> ImageRgb:
    """Add toon edges to an image.
    Edges are detected using the Canny filter, then dilated and blurred.
    The edges are then overlaid on the original image, with a given intensity and color.

    :param image: Image: Input image

    :param params: ToonEdgesParams: Parameters for the Toon Edges function

    :return Image: Image with edges overlaid
    """
    start_time = time.time()
    edges = canny(
        image,
        params.canny.t_lower,
        params.canny.t_upper,
        params.canny.aperture_size,
        params.canny.l2_gradient,
        params.canny.blur_sigma,
    )
    duration_canny = time.time() - start_time

    start_time = time.time()
    dilated_edges = dilate(
        edges,
        params.dilate.kernel_size,
        params.dilate.morph_shape,
        params.dilate.iterations,
    )
    duration_dilate = time.time() - start_time

    start_time = time.time()
    if params.appearance.blur_sigma > 0:
        dilated_edges = cv2.GaussianBlur(
            dilated_edges, (0, 0), sigmaX=params.appearance.blur_sigma, sigmaY=params.appearance.blur_sigma
        )  # type: ignore
    duration_blur = time.time() - start_time

    start_time = time.time()
    image_with_edges = merge_toon_edges(image, dilated_edges, params.appearance.intensity, params.appearance.color)
    duration_merge = time.time() - start_time

    # fiat_tuning: add debug internals to ease fine-tuning the function inside the node
    from fiatlight.fiat_kits.fiat_image import ImageWithGui

    # Add to fiat_tuning any variable you want to be able to fine-tune or debug in the function node
    #     * Either a raw type (int, float, str, etc.): see durations
    #     * Or a descendant of AnyDataWithGui: see "canny", "dilate", "image_with_edges"
    fl.add_fiat_attributes(
        add_toon_edges,
        fiat_tuning={
            "duration_canny": duration_canny,
            "duration_dilate": duration_dilate,
            "duration_blur": duration_blur,
            "duration_merge": duration_merge,
            "canny": ImageWithGui(edges),
            "dilate": ImageWithGui(dilated_edges),
            "image_with_edges": ImageWithGui(image_with_edges),
        },
    )

    # return
    return image_with_edges


def main() -> None:
    fl.run([image_from_url, add_toon_edges], fl.FiatRunParams(app_name="Toon Edges", theme=fl.ImGuiTheme_.material_flat))


if __name__ == "__main__":
    main()
