"""Dear ImGui's standard draw callbacks without a renderer backend: the checks say so, and adding one raises an error
that names the check"""

from typing import Iterator

import pytest

from imgui_bundle import imgui

NAMES = ["set_sampler_nearest", "set_sampler_linear", "set_sampler_from_tex", "reset_render_state"]


@pytest.fixture
def draw_list() -> Iterator[imgui.ImDrawList]:
    context = imgui.create_context()
    io = imgui.get_io()
    io.display_size = imgui.ImVec2(100, 100)
    io.backend_flags |= imgui.BackendFlags_.renderer_has_textures  # no backend: nothing to upload the fonts
    imgui.new_frame()
    imgui.begin("Window")
    yield imgui.get_window_draw_list()
    imgui.end()
    imgui.end_frame()
    imgui.destroy_context(context)


@pytest.mark.parametrize("name", NAMES)
def test_without_backend(draw_list: imgui.ImDrawList, name: str) -> None:
    assert getattr(imgui.get_platform_io(), f"has_draw_callback_{name}")() is False
    with pytest.raises(RuntimeError, match=f"has_draw_callback_{name}"):
        getattr(draw_list, name)()
