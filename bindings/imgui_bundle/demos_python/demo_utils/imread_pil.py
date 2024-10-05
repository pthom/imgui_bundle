from PIL import Image
import numpy as np


def imread_pil(image_file: str, convert_to_bgr: bool = False, load_alpha: bool = False) -> np.ndarray:
    """Read an image from a file using PIL, returns a numpy array."""
    image_pil = Image.open(image_file)

    def rgb_to_bgr(image: np.ndarray) -> np.ndarray:
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
