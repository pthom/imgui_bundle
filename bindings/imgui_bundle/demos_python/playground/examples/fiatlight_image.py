"""# Fiatlight: Image Pipeline

[Fiatlight](https://pthom.github.io/fiatlight/) turns Python functions into interactive apps with visual
pipelines.

This demo shows an image processing pipeline:
- download an image
- apply edge detection
- dilate
Each step displays its result and enable to
tweak the parameters.

=======================================
        Instructions
=======================================
In the node editor:
  * Use the mouse wheel to zoom/unzom
  * Right click and drag to pan the graph
In the images:
  * Use the mouse wheel to zoom/unzom
  * Left-click and drag to pan
  * Drag the bottom-right corner to resize
In the functions' cells:
  * Click on + to set a parameter value
    (to a value different from its
    default)
Click "Run" to download a new image!

**Note**
Fiatlight works best on desktop
where it auto-saves data and layout

"""
# =============================================================================
#         Part 1 - Standard Image Processing functions
#  - Here we are dealing with normal function (no user interface)
#  - However, our function use the types ImageU8 and ImageU8_GRAY, which are
#    **just aliases for numpy arrays**
#    Fiatlight will use these as an indication that it should show these arrays
#    as images
# =============================================================================
from fiatlight.fiat_kits.fiat_image import ImageU8, ImageU8_GRAY
from imgui_bundle import immapp
from enum import Enum
import cv2
import numpy as np



def download_random_image() -> ImageU8:
    """Each run downloads a different random image from [picsum.photos](https://picsum.photos/)

    > [!TIP]
    > * Inside "Dear ImGui Bundle Playground", click the "Run" button to download a new image!
    > * Zoom the image with the wheel, and pan it by dragging the mouse
    """
    def _decode_image(image_bytes: bytes) -> ImageU8:
        """Decode JPEG/PNG bytes to numpy array, with fallback test pattern."""
        if len(image_bytes) > 0:
            return cv2.imdecode(  # type: ignore
                np.frombuffer(image_bytes, dtype=np.uint8),
                cv2.IMREAD_COLOR)
        # Fallback: colorful test pattern
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        for i in range(480):
            for j in range(640):
                img[i, j] = (i % 256, j % 256, (i + j) % 256)
        return img  # type: ignore

    _IMAGE_URL = "https://picsum.photos/640/480"
    return _decode_image(immapp.download_url_bytes(_IMAGE_URL))


class CannyApertureSize(Enum):
    APERTURE_3 = 3
    APERTURE_5 = 5
    APERTURE_7 = 7


def canny(
        image: ImageU8,
        t_lower: float = 1000.0,
        t_upper: float = 5000.0,
        aperture_size: CannyApertureSize = CannyApertureSize.APERTURE_5,
        l2_gradient: bool = True,
        blur_sigma: float = 0.0,
) -> ImageU8_GRAY:
    """Performs a [canny edge detection](https://en.wikipedia.org/wiki/Canny_edge_detector) on the image after blurring it.
    There are many [parameters](https://docs.opencv.org/4.x/dd/d1a/group__imgproc__feature.html#ga04723e007ed888ddf11d9ba04e2232de),
    and finding the right ones can be tricky. See also the [OpenCV tutorial](https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html).

    Here, you can experiment with all parameters, with an instant feedback.
    """
    if blur_sigma is not None and blur_sigma > 0:
        image = cv2.GaussianBlur(image, (0, 0), sigmaX=blur_sigma, sigmaY=blur_sigma)  # type: ignore
    r = cv2.Canny(image, t_lower, t_upper, apertureSize=aperture_size.value, L2gradient=l2_gradient)  # type = ignoe
    return r  # type: ignore


class MorphShape(Enum):
    """An enum that describe the different dilatation kernel we can use"""
    MORPH_RECT = cv2.MORPH_RECT
    MORPH_CROSS = cv2.MORPH_CROSS
    MORPH_ELLIPSE = cv2.MORPH_ELLIPSE


def dilate(
        image: ImageU8_GRAY,
        kernel_size: int = 2,
        morph_shape: MorphShape = MorphShape.MORPH_ELLIPSE,
        iterations: int = 1,
) -> ImageU8_GRAY:
    """[Dilate](https://en.wikipedia.org/wiki/Dilation_(morphology)) the image using the specified kernel shape and size

    This is often used to increase the thickness of detected objects in an image.
    See [OpenCV tutorial](https://docs.opencv.org/4.x/db/df6/tutorial_erosion_dilatation.html) and [parameters](https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html#ga4ff0f3318642c4f469d0e11f242f3b6c)

    *Note: if kernel_size is 1, the dilation will do nothing.*
    """
    kernel = cv2.getStructuringElement(morph_shape.value, (kernel_size, kernel_size))
    r = cv2.dilate(image, kernel, iterations=iterations)
    return r  # type: ignore



# =============================================================================
#         Part 2 - Define a GUI with Fiatlight
#  - Here we import fiatlight, and add attributes to functions, then run the app
# =============================================================================
import fiatlight as fl  # noqa

# Add attributes to the canny function, specifying the ranges
fl.add_fiat_attributes(
    canny,
    blur_sigma__range=(0.0, 10.0),
    blur_sigma__tooltip="blur_sigma controls the amount of Gaussian blur applied to the image before edge detection "
                        "(0: no blur). More blur: fewer, smoother edges.",
    t_lower__range=(100.0, 10000.0),
    t_lower__slider_logarithmic=True,
    t_lower__tooltip="The lower threshold: a pixel whose gradient is below it is never an edge. A pixel between the two "
                     "thresholds is an edge only when it touches a pixel above the upper one.",
    t_upper__range=(100.0, 10000.0),
    t_upper__slider_logarithmic=True,
    t_upper__tooltip="The upper threshold: a pixel whose gradient is above it is always an edge. Raise it for fewer edges.",
    aperture_size__tooltip="The size of the Sobel kernel that computes the gradient. A larger kernel gives larger "
                           "gradients: the thresholds must follow.",
    l2_gradient__tooltip="Measure the gradient with the exact norm, sqrt(gx^2 + gy^2), instead of |gx| + |gy| "
                         "(faster, less precise).",
)
fl.add_fiat_attributes(
    CannyApertureSize,
    APERTURE_3__tooltip="A 3x3 Sobel kernel",
    APERTURE_5__tooltip="A 5x5 Sobel kernel",
    APERTURE_7__tooltip="A 7x7 Sobel kernel",
)

# Add attributes to the dilate function, specifying the ranges
# (note: the MorphShape enum is automatically handled as radio buttons)
fl.add_fiat_attributes(
    dilate,
    kernel_size__range=(1, 10),
    kernel_size__tooltip="The size of the kernel, in pixels: the larger, the thicker the lines (1: no dilation).",
    morph_shape__tooltip="The shape of the kernel: it gives its shape to the thickened lines.",
    iterations__range=(1, 10),
    iterations__tooltip="How many times the dilation is applied: each time, the lines get thicker.",
)
fl.add_fiat_attributes(
    MorphShape,
    MORPH_RECT__tooltip="A rectangle: square corners",
    MORPH_CROSS__tooltip="A cross: lines grow along the horizontal and the vertical",
    MORPH_ELLIPSE__tooltip="An ellipse: rounded, the most natural thickening",
)


fl.run([download_random_image, canny, dilate], app_name="demo_canny")
