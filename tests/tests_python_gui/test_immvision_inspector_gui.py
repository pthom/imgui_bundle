"""ImmVision's inspector shows an image added before the app runs, and one added inside a frame."""

import numpy as np
from PIL import Image

from imgui_bundle import immvision
from imgui_bundle.immapp import testing


def solid(rgb: tuple[int, int, int]) -> np.ndarray:
    image = np.zeros((64, 64, 3), np.uint8)
    image[...] = rgb
    return image


def count_pixels(image: np.ndarray, rgb: tuple[int, int, int]) -> int:
    return int((np.abs(image - np.array(rgb)).sum(axis=2) < 30).sum())


def test_inspector_images_added_before_the_app_and_inside_a_frame(tmp_path) -> None:  # type: ignore[no-untyped-def]
    red, green = (255, 0, 0), (0, 255, 0)
    immvision.inspector_add_image(solid(red), "before the app")  # no OpenGL context yet
    added: list[bool] = []

    def gui() -> None:
        if not added:
            immvision.inspector_add_image(solid(green), "inside a frame")
            added.append(True)
        immvision.inspector_show()

    try:
        path = testing.capture_final_frame(gui, tmp_path / "inspector.png", window_size=(800, 600))
    finally:
        immvision.inspector_clear_images()

    shot = np.asarray(Image.open(path).convert("RGB"), dtype=np.int32)
    scale = shot.shape[1] // 800  # 2 on a Retina screen
    # The first image, selected, fills the main view; the second one shows in the filmstrip, as a thumbnail
    assert count_pixels(shot, red) > 20000 * scale * scale, "the image added before the app is not shown"
    assert count_pixels(shot, green) > 500 * scale * scale, "the image added inside a frame is not in the filmstrip"
