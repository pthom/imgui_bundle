import numpy as np
from numpy.typing import NDArray


_HAS_PIL = False
try:
    from PIL import Image
    _HAS_PIL = True
except ImportError:
    import logging
    logging.error("""
        pillow is required to read images for Dear ImGui Bundle demo (using demo pattern instead). Install it with:
            pip install pillow   # or conda install pillow
        """)


def _dummy_image(with_alpha: bool) -> NDArray[np.uint8]:
    """
    Generates a 400x400 RGBA image with a visually appealing sine wave interference pattern
    and a transparent background.
    """
    width, height = 400, 400

    # Create a grid of x and y coordinates
    x = np.linspace(-1 * np.pi, 1 * np.pi, width)
    y = np.linspace(-1 * np.pi, 1 * np.pi, height)
    X, Y = np.meshgrid(x, y)

    # Calculate sine wave interference pattern
    pattern = np.sin(X**2 + Y**2) + np.sin(3 * X + 2.5 * Y)

    # Normalize the pattern to range [0, 1]
    normalized_pattern = (pattern - pattern.min()) / (pattern.max() - pattern.min())

    # Map the pattern to RGB colors
    R = (np.sin(2 * np.pi * normalized_pattern) * 127 + 128).astype(np.uint8)
    G = (np.cos(3 * np.pi * normalized_pattern + np.pi / 2) * 127 + 128).astype(np.uint8)
    B = (np.sin(2 * np.pi * normalized_pattern + np.pi) * 127 + 128).astype(np.uint8)

    # Combine into an RGB image
    rgb_image = np.dstack((R, G, B))

    if not with_alpha:
        return rgb_image

    # Create an alpha channel: fully opaque for non-zero patterns
    alpha = (normalized_pattern > 0.15).astype(np.uint8) * 255

    # Combine RGB and alpha channels into RGBA
    rgba_image = np.dstack((rgb_image, alpha))

    return rgba_image




def imread_pil(image_file: str, convert_to_bgr: bool = False, load_alpha: bool = False) -> NDArray[np.uint]:
    """Read an image from a file using PIL, returns a numpy array."""
    if not _HAS_PIL:
        return _dummy_image(load_alpha)

    image_pil = Image.open(image_file)

    def rgb_to_bgr(image: NDArray[np.uint]) -> NDArray[np.uint]:
        assert len(image.shape) == 3
        if image.shape[2] == 3:
            return np.ascontiguousarray(image[:, :, ::-1])
        elif image.shape[2] == 4:
            bgr = image[:, :, :3][:, :, ::-1]
            a = image[:, :, 3]
            bgra = np.dstack((bgr, a))
            return np.ascontiguousarray(bgra)
        else:
            raise ValueError("Invalid shape")

    if load_alpha:
        image = np.array(image_pil.convert("RGBA"))
    else:
        image = np.array(image_pil.convert("RGB"))

    if convert_to_bgr:
        image = rgb_to_bgr(image)

    return image
