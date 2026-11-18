"""Dear ImGui's standard draw callbacks on Hello ImGui's renderer: nearest sampling keeps the pixels of a small image
shown large, linear sampling blends them, and set_sampler_from_tex() keeps the filter of an OpenGL texture. And the
demo runs."""

import numpy as np
import pytest
from PIL import Image

from imgui_bundle import imgui
from imgui_bundle.immapp import testing

SIZE = 100  # each image's width and height on screen, in logical pixels


def test_nearest_and_linear_sampling(tmp_path) -> None:  # type: ignore[no-untyped-def]
    # A 2x2 checkerboard, black and white, drawn twice: with nearest sampling, then with linear sampling
    texture = imgui.ImTextureData()
    checkerboard = np.array([[0, 0, 0, 255], [255, 255, 255, 255], [255, 255, 255, 255], [0, 0, 0, 255]], np.uint8)
    supported = {}

    def gui() -> None:
        if texture.status == imgui.ImTextureStatus.destroyed:
            texture.create(imgui.ImTextureFormat.rgba32, 2, 2)
            texture.get_pixels_array()[:] = checkerboard.ravel()
            imgui.internal.register_user_texture(texture)
        draw_list = imgui.get_foreground_draw_list()
        supported["nearest"] = draw_list.can_set_sampler_nearest()
        supported["linear"] = draw_list.can_set_sampler_linear()
        draw_list.set_sampler_nearest()
        draw_list.add_image(texture.get_tex_ref(), (0, 0), (SIZE, SIZE))
        draw_list.set_sampler_linear()
        draw_list.add_image(texture.get_tex_ref(), (SIZE, 0), (2 * SIZE, SIZE))

    path = testing.capture_final_frame(gui, tmp_path / "sampling.png", window_size=(2 * SIZE, SIZE))
    assert supported == {"nearest": True, "linear": True}

    gray = np.asarray(Image.open(path).convert("L"), dtype=np.int32)
    scale = gray.shape[1] // (2 * SIZE)  # 2 on a Retina screen
    row = gray[SIZE * scale // 4]  # across the top row of the checkerboard's cells
    nearest, linear = row[: SIZE * scale], row[SIZE * scale :]
    is_gray = (row > 20) & (row < 235)
    assert not is_gray[: SIZE * scale].any(), f"nearest: only black and white expected, got {np.unique(nearest)}"
    # Linear sampling blends between the texels' centers: a gradient across about half of the image
    assert is_gray[SIZE * scale :].sum() > SIZE * scale // 4, f"linear: a gradient expected, got {np.unique(linear)}"


def test_sampler_from_tex(tmp_path) -> None:  # type: ignore[no-untyped-def]
    # A 2x2 checkerboard made with OpenGL, with its own filter GL_NEAREST: set_sampler_from_tex() keeps it sharp,
    # frame after frame. reset_render_state() comes back to linear sampling without writing into the texture's filter
    # (a set_sampler_linear() there would: the image was sharp in the first frame only).
    gl = pytest.importorskip("OpenGL.GL")
    checkerboard = np.array([[0, 0, 0, 255], [255, 255, 255, 255], [255, 255, 255, 255], [0, 0, 0, 255]], np.uint8)
    texture_id = {"id": 0}
    supported = {}

    def gui() -> None:
        if texture_id["id"] == 0:
            texture_id["id"] = int(gl.glGenTextures(1))
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id["id"])
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, 2, 2, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, checkerboard)
        draw_list = imgui.get_foreground_draw_list()
        supported["from_tex"] = draw_list.can_set_sampler_from_tex()
        draw_list.set_sampler_from_tex()
        draw_list.add_image(imgui.ImTextureRef(texture_id["id"]), (0, 0), (SIZE, SIZE))
        draw_list.reset_render_state()
        draw_list.add_image(imgui.ImTextureRef(texture_id["id"]), (SIZE, 0), (2 * SIZE, SIZE))

    path = testing.capture_final_frame(gui, tmp_path / "from_tex.png", window_size=(2 * SIZE, SIZE))
    assert supported == {"from_tex": True}

    gray = np.asarray(Image.open(path).convert("L"), dtype=np.int32)
    scale = gray.shape[1] // (2 * SIZE)
    row = gray[SIZE * scale // 4]
    is_gray = (row > 20) & (row < 235)
    assert not is_gray[: SIZE * scale].any(), f"from_tex: only black and white expected, got {np.unique(row)}"
    assert is_gray[SIZE * scale :].sum() > SIZE * scale // 4, "linear: the renderer's sampling overrides GL_NEAREST"


def test_demo_runs(tmp_path) -> None:  # type: ignore[no-untyped-def]
    from imgui_bundle.demos_python.demos_immapp import demo_sampler_callbacks

    testing.capture_final_frame(demo_sampler_callbacks.gui, tmp_path / "demo.png", with_markdown=True)
