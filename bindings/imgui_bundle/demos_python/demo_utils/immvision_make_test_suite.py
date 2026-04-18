# Rendering test suite for ImmVision: exercises all depth/channel code paths.
# Used as a visual reference before and after the OpenCV removal migration.
#
# Python port of demos_cpp/demos_immvision/demo_immvision_rendering_test.cpp

import math
import importlib.util
import numpy as np
from imgui_bundle import immvision
from imgui_bundle.demos_python import demo_utils

HAS_OPENCV = importlib.util.find_spec("cv2") is not None


def _make_synthetic_gradient(
        w: int, h: int, channels: int, dtype: np.dtype, min_val: float, max_val: float
) -> np.ndarray:
    """Horizontal gradient + vertical sine pattern."""
    shape = (h, w, channels) if channels > 1 else (h, w)
    mat = np.zeros(shape, dtype=dtype)

    for y in range(h):
        vy = 0.5 + 0.3 * math.sin(2.0 * math.pi * y / h * 4.0)
        for x in range(w):
            t = x / (w - 1)
            val = min_val + (max_val - min_val) * t * vy
            for c in range(channels):
                channel_offset = (c - 1) * (max_val - min_val) * 0.1 if channels > 1 else 0.0
                v = max(min_val, min(max_val, val + channel_offset))
                if channels > 1:
                    mat[y, x, c] = dtype.type(v)
                else:
                    mat[y, x] = dtype.type(v)
    return mat


def immvision_make_test_suite() -> None:
    assets_dir = demo_utils.demos_assets_folder() + "/images/"
    zoom_key = "zk"

    # File-based images
    house = immvision.im_read(assets_dir + "house.jpg")
    if house.size > 0:
        immvision.inspector_add_image(house, "house_rgb_u8", zoom_key)

        if HAS_OPENCV:
            import cv2
            house_bgr = cv2.cvtColor(house, cv2.COLOR_RGB2BGR)  # type: ignore[arg-type]
            gray = cv2.cvtColor(house_bgr, cv2.COLOR_BGR2GRAY)
            immvision.inspector_add_image(gray, "house_gray_u8", zoom_key)

            # Floyd-Steinberg dithered halftone
            fs = gray.astype(np.float32)
            for y in range(fs.shape[0]):
                for x in range(fs.shape[1]):
                    old_val = fs[y, x]
                    new_val = 255.0 if old_val > 127.5 else 0.0
                    err = old_val - new_val
                    fs[y, x] = new_val
                    if x + 1 < fs.shape[1]:
                        fs[y, x + 1] += err * 7.0 / 16.0
                    if y + 1 < fs.shape[0] and x > 0:
                        fs[y + 1, x - 1] += err * 3.0 / 16.0
                    if y + 1 < fs.shape[0]:
                        fs[y + 1, x] += err * 5.0 / 16.0
                    if y + 1 < fs.shape[0] and x + 1 < fs.shape[1]:
                        fs[y + 1, x + 1] += err * 1.0 / 16.0
            immvision.inspector_add_image(
                np.clip(fs, 0, 255).astype(np.uint8), "house_gray_halftone", zoom_key
            )

            blur = cv2.GaussianBlur(gray, (0, 0), 7.0)
            immvision.inspector_add_image(blur, "house_blur_u8", zoom_key)

            float_mat = blur.astype(np.float64) / 255.0
            immvision.inspector_add_image(float_mat, "house_f64", zoom_key)

            # Sobel gradient magnitude
            sobel_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
            sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
            sobel_mag = np.sqrt(sobel_x**2 + sobel_y**2)
            max_val = sobel_mag.max()
            if max_val > 0:
                sobel_mag = sobel_mag / max_val
            immvision.inspector_add_image(sobel_mag, "house_sobel_f32", zoom_key)

    bear = immvision.im_read(assets_dir + "bear_transparent.png")
    if bear.size > 0:
        immvision.inspector_add_image(bear, "bear_rgba_u8")

    tennis = immvision.im_read(assets_dir + "tennis.jpg")
    if tennis.size > 0:
        immvision.inspector_add_image(tennis, "tennis_rgb_u8")

    # Synthetic: uint8 variants
    immvision.inspector_add_image(
        _make_synthetic_gradient(200, 150, 3, np.dtype("uint8"), 0, 255),
        "synth_u8_3ch",
    )
    immvision.inspector_add_image(
        _make_synthetic_gradient(200, 150, 1, np.dtype("uint8"), 0, 255),
        "synth_u8_1ch",
    )
    immvision.inspector_add_image(
        _make_synthetic_gradient(200, 150, 2, np.dtype("uint8"), 0, 255),
        "synth_u8_2ch",
    )

    # 4-channel RGBA with gradient alpha
    rgba = np.zeros((150, 200, 4), dtype=np.uint8)
    for y in range(150):
        for x in range(200):
            rgba[y, x, 0] = x * 255 // 199  # R
            rgba[y, x, 1] = y * 255 // 149  # G
            rgba[y, x, 2] = 128  # B
            rgba[y, x, 3] = x * 255 // 199  # A
    immvision.inspector_add_image(rgba, "synth_u8_4ch_rgba")

    # Synthetic: signed/unsigned integer depths
    immvision.inspector_add_image(
        _make_synthetic_gradient(200, 150, 1, np.dtype("int8"), -128, 127),
        "synth_s8_1ch",
    )
    immvision.inspector_add_image(
        _make_synthetic_gradient(200, 150, 1, np.dtype("uint16"), 0, 65535),
        "synth_u16_1ch",
    )
    immvision.inspector_add_image(
        _make_synthetic_gradient(200, 150, 1, np.dtype("int16"), -32768, 32767),
        "synth_s16_1ch",
    )
    immvision.inspector_add_image(
        _make_synthetic_gradient(200, 150, 1, np.dtype("int32"), -2147483648, 2147483647),
        "synth_s32_1ch",
    )

    # Synthetic: float depths
    immvision.inspector_add_image(
        _make_synthetic_gradient(200, 150, 1, np.dtype("float32"), -1.0, 1.0),
        "synth_f32_1ch",
    )
    immvision.inspector_add_image(
        _make_synthetic_gradient(200, 150, 3, np.dtype("float32"), 0.0, 1.0),
        "synth_f32_3ch",
    )
    immvision.inspector_add_image(
        _make_synthetic_gradient(200, 150, 1, np.dtype("float64"), -1.0, 1.0),
        "synth_f64_1ch",
    )
    immvision.inspector_add_image(
        _make_synthetic_gradient(200, 150, 3, np.dtype("float64"), 0.0, 1.0),
        "synth_f64_3ch",
    )

    # Synthetic: edge cases — checkerboard
    checker = np.zeros((200, 200), dtype=np.uint8)
    for y in range(200):
        for x in range(200):
            checker[y, x] = 255 if ((x // 8) + (y // 8)) % 2 == 0 else 0
    immvision.inspector_add_image(checker, "synth_checker_u8")

    # Halftone-like binary pattern
    halftone = np.zeros((300, 300), dtype=np.uint8)
    for y in range(300):
        for x in range(300):
            intensity = x / 299.0
            threshold = ((x % 4) * 4 + (y % 4)) * 255 / 16
            halftone[y, x] = 255 if intensity * 255 > threshold else 0
    immvision.inspector_add_image(halftone, "synth_halftone")

    # Float32 with special values: NaN, +Inf, -Inf
    special = np.zeros((100, 100), dtype=np.float32)
    for y in range(100):
        for x in range(100):
            if x < 25:
                special[y, x] = y / 99.0
            elif x < 50:
                special[y, x] = np.nan
            elif x < 75:
                special[y, x] = np.inf
            else:
                special[y, x] = -np.inf
    immvision.inspector_add_image(special, "synth_f32_special")
