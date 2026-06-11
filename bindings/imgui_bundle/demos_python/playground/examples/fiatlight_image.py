"""# Fiatlight: Image Pipeline

Fiatlight turns Python functions into
interactive apps with visual pipelines.
https://pthom.github.io/fiatlight

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
    """Synchronous download of a random image"""
    # Each run downloads a different random image from picsum.photos
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
    APERTURE_3 = (3,)
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
    """Performs a canny edge detection on the image after bluring it
    There are many parameters, and finding the right ones can be tricky.
    Fiatlight user interface can help with this.
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
    """Dilate the image using the specified kernel shape and size

    This is often used to increase the thickness of detected objects in an image.
    Note: if kernel_size is 1, the dilation will do nothing.
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
    t_lower__range=(100.0, 10000.0),
    t_lower__slider_logarithmic=True,
    t_upper__range=(100.0, 10000.0),
    t_upper__slider_logarithmic=True,
)

# Add attributes to the dilate function, specifying the ranges
# (note: the MorphShape enum is automatically handled as radio buttons)
fl.add_fiat_attributes(dilate, kernel_size__range=(1, 10), iterations__range=(1, 10))


fl.run([download_random_image, canny, dilate], app_name="demo_canny")
