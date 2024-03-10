# demo_tex_inspect_simple
# See equivalent C++ program: demos_cpp/demos_tex_inspect/demo_tex_inspect_simple.cpp
from imgui_bundle import imgui_tex_inspect, ImVec2, immapp, hello_imgui

from imgui_bundle.demos_python.demo_utils.api_demos import (
    set_hello_imgui_demo_assets_folder,
)


@immapp.static(texture_id=None)
def demo_gui():
    static = demo_gui

    if static.texture_id is None:
        static.texture_id = hello_imgui.im_texture_id_from_asset(
            "images/bear_transparent.png"
        )

    texture_size = ImVec2(512.0, 512.0)

    flags = 0
    inspector_size = imgui_tex_inspect.SizeIncludingBorder(immapp.em_to_vec2(30, 30))
    if imgui_tex_inspect.begin_inspector_panel(
        "Texture Inspector", static.texture_id, texture_size, flags, inspector_size
    ):
        pass # nothing to do here
    imgui_tex_inspect.end_inspector_panel() # Always call end_inspector_panel() even if begin_inspector_panel() returns false


def main():
    set_hello_imgui_demo_assets_folder()
    immapp.run(
        demo_gui, with_tex_inspect=True, with_markdown=True, window_size=(1200, 1000)
    )


if __name__ == "__main__":
    main()
