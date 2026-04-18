"""Tests for the ImmVision nanobind type casters.

Tests that ImageBuffer <-> numpy, Point/Point2d/Size <-> tuple,
and Matrix33d <-> list[list[float]] work correctly, including
zero-copy behavior, dtype preservation, and edge cases.

Run with: pytest test_immvision_type_casters.py -v
(Requires imgui_bundle built with immvision support)
"""

import numpy as np
import pytest
from imgui_bundle import immvision

th = immvision._test_helpers


# =========================================================================
# ImageBuffer <-> numpy: zero-copy round-trip
# =========================================================================

def test_roundtrip_preserves_data_pointer():
    """Round-trip through C++ should not copy data (zero-copy)."""
    img = np.zeros((10, 20, 3), dtype=np.uint8)
    ptr_before = img.ctypes.data
    result = th.roundtrip(img)
    ptr_after = result.ctypes.data
    assert ptr_before == ptr_after


def test_roundtrip_preserves_values():
    """Round-trip should preserve pixel values exactly."""
    img = np.arange(60, dtype=np.float32).reshape(3, 4, 5)
    result = th.roundtrip(img)
    np.testing.assert_array_equal(img, result)


# =========================================================================
# ImageBuffer <-> numpy: all dtypes
# =========================================================================

ALL_DTYPES = [np.uint8, np.int8, np.uint16, np.int16, np.int32, np.float32, np.float64]
# ImageDepth enum values: uint8=0, int8=1, uint16=2, int16=3, int32=4, float32=5, float64=6
DTYPE_TO_DEPTH_INT = {
    np.uint8: 0, np.int8: 1, np.uint16: 2, np.int16: 3,
    np.int32: 4, np.float32: 5, np.float64: 6,
}


@pytest.mark.parametrize("dtype", ALL_DTYPES, ids=[d.__name__ for d in ALL_DTYPES])
def test_dtype_roundtrip(dtype):
    """Each numpy dtype should round-trip correctly through ImageBuffer."""
    img = np.ones((8, 12), dtype=dtype)
    result = th.roundtrip(img)
    assert result.dtype == dtype
    np.testing.assert_array_equal(img, result)


@pytest.mark.parametrize("dtype", ALL_DTYPES, ids=[d.__name__ for d in ALL_DTYPES])
def test_dtype_detected_correctly(dtype):
    """C++ should detect the correct ImageDepth from numpy dtype."""
    img = np.ones((4, 5), dtype=dtype)
    w, h, ch, depth_int = th.image_info(img)
    assert w == 5
    assert h == 4
    assert ch == 1
    assert depth_int == DTYPE_TO_DEPTH_INT[dtype]


# =========================================================================
# ImageBuffer <-> numpy: channel variants
# =========================================================================

def test_1channel_shape():
    """1-channel image: C++ sees channels=1, returns shape (H, W)."""
    img = np.zeros((10, 20), dtype=np.uint8)
    w, h, ch, _ = th.image_info(img)
    assert (w, h, ch) == (20, 10, 1)
    result = th.roundtrip(img)
    assert result.shape == (10, 20)


def test_3channel_shape():
    """3-channel image: C++ sees channels=3, returns shape (H, W, 3)."""
    img = np.zeros((10, 20, 3), dtype=np.uint8)
    w, h, ch, _ = th.image_info(img)
    assert (w, h, ch) == (20, 10, 3)
    result = th.roundtrip(img)
    assert result.shape == (10, 20, 3)


def test_4channel_shape():
    """4-channel RGBA: C++ sees channels=4, returns shape (H, W, 4)."""
    img = np.zeros((10, 20, 4), dtype=np.uint8)
    w, h, ch, _ = th.image_info(img)
    assert (w, h, ch) == (20, 10, 4)
    result = th.roundtrip(img)
    assert result.shape == (10, 20, 4)


# =========================================================================
# ImageBuffer: C++ creates and returns owned data
# =========================================================================

def test_create_from_cpp():
    """ImageBuffer::Zeros created in C++ should arrive as a valid numpy array."""
    result = th.create_test_image(30, 20, 3, 0)  # 0 = uint8
    assert isinstance(result, np.ndarray)
    assert result.shape == (20, 30, 3)
    assert result.dtype == np.uint8
    assert np.all(result == 0)


@pytest.mark.parametrize("dtype,depth_int", [
    (np.uint8, 0), (np.int8, 1), (np.uint16, 2), (np.int16, 3),
    (np.int32, 4), (np.float32, 5), (np.float64, 6),
], ids=["uint8", "int8", "uint16", "int16", "int32", "float32", "float64"])
def test_create_from_cpp_all_dtypes(dtype, depth_int):
    """C++-created ImageBuffer should have correct dtype for all depths."""
    result = th.create_test_image(10, 10, 1, depth_int)
    assert result.dtype == dtype


# =========================================================================
# ImageBuffer: lifetime / _ref_keeper
# =========================================================================

def test_holder_keeps_data_alive():
    """Data stored in a C++ TestHolder should survive after Python array is deleted."""
    holder = th.TestHolder()
    img = np.arange(12, dtype=np.float32).reshape(3, 4)
    holder.store(img)
    del img  # Python array goes away
    result = holder.retrieve()
    expected = np.arange(12, dtype=np.float32).reshape(3, 4)
    np.testing.assert_array_equal(result, expected)


def test_holder_zero_copy():
    """Storing in TestHolder should be zero-copy (same data pointer)."""
    holder = th.TestHolder()
    img = np.zeros((5, 5), dtype=np.uint8)
    ptr = img.ctypes.data
    holder.store(img)
    result = holder.retrieve()
    assert result.ctypes.data == ptr


# =========================================================================
# Non-contiguous array rejection
# =========================================================================

def test_non_contiguous_rejected():
    """Non-contiguous numpy arrays should be rejected."""
    img = np.zeros((20, 20, 3), dtype=np.uint8)
    non_contiguous = img[::2, ::2, :]
    assert not non_contiguous.flags['C_CONTIGUOUS']
    with pytest.raises((TypeError, RuntimeError)):
        th.roundtrip(non_contiguous)


# =========================================================================
# Point / Point2d / Size / Matrix33d direct round-trips
# =========================================================================

def test_point_roundtrip():
    """Point round-trip through C++."""
    result = th.roundtrip_point((42, 99))
    assert result == (42, 99)
    assert isinstance(result, tuple)


def test_point2d_roundtrip():
    """Point2d round-trip through C++."""
    result = th.roundtrip_point2d((3.14, 2.71))
    assert result[0] == pytest.approx(3.14)
    assert result[1] == pytest.approx(2.71)
    assert isinstance(result, tuple)


def test_size_roundtrip():
    """Size round-trip through C++."""
    result = th.roundtrip_size((640, 480))
    assert result == (640, 480)
    assert isinstance(result, tuple)


def test_matrix33d_roundtrip_list():
    """Matrix33d round-trip with list[list[float]]."""
    m = [[2, 0, 10], [0, 3, 20], [0, 0, 1]]
    result = th.roundtrip_matrix33d(m)
    assert isinstance(result, list)
    assert result[0][0] == pytest.approx(2.0)
    assert result[0][2] == pytest.approx(10.0)
    assert result[1][1] == pytest.approx(3.0)


def test_matrix33d_roundtrip_numpy():
    """Matrix33d round-trip with numpy array input."""
    m = np.eye(3) * 5.0
    result = th.roundtrip_matrix33d(m)
    assert isinstance(result, list)  # always returns list
    assert result[0][0] == pytest.approx(5.0)
    assert result[1][1] == pytest.approx(5.0)
    assert result[0][1] == pytest.approx(0.0)


# =========================================================================
# Point / Point2d / Size via ImageParams members
# =========================================================================

def test_point_in_watched_pixels():
    """WatchedPixels is List[Point] = List[Tuple[int, int]]."""
    params = immvision.ImageParams()
    params.watched_pixels = [(10, 20), (30, 40)]
    assert params.watched_pixels == [(10, 20), (30, 40)]


def test_size_in_image_params():
    """ImageParams.image_display_size is Size = Tuple[int, int]."""
    params = immvision.ImageParams(image_display_size=(320, 240))
    assert params.image_display_size == (320, 240)


def test_matrix33d_in_image_params():
    """ZoomPanMatrix accepts list and numpy."""
    params = immvision.ImageParams()
    params.zoom_pan_matrix = [[2, 0, 50], [0, 2, 60], [0, 0, 1]]
    m = params.zoom_pan_matrix
    assert m[0][0] == pytest.approx(2.0)

    params.zoom_pan_matrix = np.eye(3) * 4.0
    m = params.zoom_pan_matrix
    assert m[0][0] == pytest.approx(4.0)


def test_matrix33d_default_is_identity():
    """Default ZoomPanMatrix should be identity."""
    params = immvision.ImageParams()
    m = params.zoom_pan_matrix
    for i in range(3):
        for j in range(3):
            expected = 1.0 if i == j else 0.0
            assert m[i][j] == pytest.approx(expected)


# =========================================================================
# MakeZoomPanMatrix functions
# =========================================================================

def test_make_zoom_pan_matrix():
    m = immvision.make_zoom_pan_matrix(
        zoom_center=(50.0, 50.0), zoom_ratio=2.0, displayed_image_size=(200, 200))
    assert isinstance(m, list)
    assert m[0][0] == pytest.approx(2.0)


def test_make_zoom_pan_matrix_full_view():
    m = immvision.make_zoom_pan_matrix_full_view(
        image_size=(200, 100), displayed_image_size=(100, 50))
    assert m[0][0] == pytest.approx(0.5)


# =========================================================================
# JSON serialization round-trip
# =========================================================================

def test_json_roundtrip():
    """ImageParams with all custom types should survive JSON round-trip."""
    params = immvision.ImageParams()
    params.image_display_size = (400, 300)
    params.watched_pixels = [(10, 20), (30, 40)]
    params.zoom_pan_matrix = [[2, 0, 50], [0, 2, 60], [0, 0, 1]]
    params.show_grid = False
    params.colormap_settings.colormap = "Viridis"

    json_str = immvision.image_params_to_json(params)
    restored = immvision.image_params_from_json(json_str)

    assert restored.image_display_size == (400, 300)
    assert restored.watched_pixels == [(10, 20), (30, 40)]
    assert restored.zoom_pan_matrix[0][0] == pytest.approx(2.0)
    assert restored.zoom_pan_matrix[0][2] == pytest.approx(50.0)
    assert not restored.show_grid
    assert restored.colormap_settings.colormap == "Viridis"


# =========================================================================
# ImageParams defaults
# =========================================================================

def test_image_params_defaults():
    params = immvision.ImageParams()
    assert params.image_display_size == (0, 0)
    assert not params.refresh_image
    assert params.pan_with_mouse
    assert params.show_grid
    assert params.watched_pixels == []
    assert params.mouse_info.mouse_position == (-1.0, -1.0)


# =========================================================================
# Empty image handling
# =========================================================================

def test_empty_image_0x0():
    """Passing a 0x0 array should not crash."""
    img = np.zeros((0, 0), dtype=np.uint8)
    try:
        th.data_pointer(img)
    except (TypeError, ValueError):
        pass  # acceptable to reject


def test_empty_image_0_rows():
    """Passing an array with 0 rows should not crash."""
    img = np.zeros((0, 10), dtype=np.uint8)
    try:
        th.data_pointer(img)
    except (TypeError, ValueError):
        pass


def test_empty_image_0_cols():
    """Passing an array with 0 cols should not crash."""
    img = np.zeros((10, 0), dtype=np.uint8)
    try:
        th.data_pointer(img)
    except (TypeError, ValueError):
        pass


# =========================================================================
# Error messages on bad input
# =========================================================================

def test_reject_1d_array():
    """1D arrays should be rejected (images need at least 2D)."""
    arr = np.zeros(100, dtype=np.uint8)
    with pytest.raises(TypeError):
        th.roundtrip(arr)


def test_reject_string():
    """Passing a string should be rejected."""
    with pytest.raises(TypeError):
        th.roundtrip("not an image")


def test_reject_none():
    """Passing None should be rejected."""
    with pytest.raises(TypeError):
        th.roundtrip(None)


def test_reject_list():
    """Passing a plain list should be rejected."""
    with pytest.raises(TypeError):
        th.roundtrip([[1, 2], [3, 4]])


# =========================================================================
# Shared memory: modify from Python, visible in C++
# =========================================================================

def test_shared_memory_modify_from_python():
    """Modify numpy array after storing in C++ holder — C++ should see the change."""
    holder = th.TestHolder()
    img = np.zeros((5, 5), dtype=np.uint8)
    holder.store(img)

    # Modify from Python
    img[2, 3] = 42

    # Retrieve from C++ and verify modification is visible
    result = holder.retrieve()
    assert result[2, 3] == 42


def test_shared_memory_bidirectional():
    """Verify round-trip shares memory: modifying the result modifies the original."""
    img = np.zeros((10, 10), dtype=np.float32)
    result = th.roundtrip(img)

    # They share memory — modifying result should modify img
    result[5, 5] = 99.0
    assert img[5, 5] == 99.0


# =========================================================================
# Performance benchmark
# =========================================================================

def test_performance_benchmarks():
    """Benchmark roundtrip performance for typical image sizes.
    Verifies that zero-copy is truly zero-copy (should be < 10µs per frame)."""
    import time

    sizes = [
        ("640x480x3 (VGA RGB)", (480, 640, 3)),
        ("1920x1080x3 (HD RGB)", (1080, 1920, 3)),
    ]

    print("\n=== Performance Benchmarks ===")
    for name, shape in sizes:
        arr = np.random.randint(0, 255, shape, dtype=np.uint8)

        iterations = 1000
        start = time.perf_counter()
        for _ in range(iterations):
            th.roundtrip(arr)
        elapsed = time.perf_counter() - start

        avg_us = (elapsed / iterations) * 1_000_000
        fps = iterations / elapsed
        print(f"  {name}: {avg_us:.2f} µs/frame ({fps:.0f} FPS)")

        # Zero-copy roundtrip should be very fast (< 50µs even with overhead)
        assert avg_us < 50, f"Roundtrip too slow ({avg_us:.1f} µs), likely copying data"


# =========================================================================
# Non-contiguous cv::Mat (ROI) is cloned to contiguous in ImageBuffer
# =========================================================================

def test_non_contiguous_cvmat_cloned():
    """ImageBuffer(cv::Mat) should clone non-contiguous ROI sub-matrices
    to contiguous memory. Verify the resulting numpy array is contiguous
    and has correct shape/values."""
    result = th.create_from_non_contiguous_roi()
    assert isinstance(result, np.ndarray)
    assert result.flags['C_CONTIGUOUS']
    assert result.shape == (20, 20, 3)
    # The ROI starts at (2,2) in the original 100x100 image.
    # The known pixel was set at (5,5) in the original,
    # which is (3,3) in the ROI.
    assert result[3, 3, 0] == 42
    assert result[3, 3, 1] == 43
    assert result[3, 3, 2] == 44
    # Background pixels should be (10, 20, 30)
    assert result[0, 0, 0] == 10
    assert result[0, 0, 1] == 20
    assert result[0, 0, 2] == 30
