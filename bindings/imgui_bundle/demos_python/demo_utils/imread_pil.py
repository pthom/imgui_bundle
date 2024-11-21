import numpy as np
from numpy.typing import NDArray


def imread_pil(image_file: str, convert_to_bgr: bool = False, load_alpha: bool = False) -> NDArray[np.uint]:
    """Read an image from a file using PIL, returns a numpy array."""
    from PIL import Image
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
