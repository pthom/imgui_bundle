# demo_tex_inspect_simple
# See equivalent C++ program: demos_cpp/demos_tex_inspect/demo_tex_inspect_simple.cpp
from imgui_bundle import imgui_tex_inspect, hello_imgui
from imgui_bundle.demos.demo_utils.api_demos import *


def make_gui() -> GuiFunction:
    texture_id = None
    texture_size = ImVec2(512.0, 512.0)

    def gui():
        nonlocal texture_id
        if texture_id is None:
            texture_id = hello_imgui.im_texture_id_from_asset("images/bear_transparent.png")

        flags = 0
        inspector_size = imgui_tex_inspect.SizeIncludingBorder(immapp.em_vec2(30, 30))
        if imgui_tex_inspect.begin_inspector_panel("Texture Inspector", texture_id, texture_size, flags, inspector_size):
            imgui_tex_inspect.end_inspector_panel()

    return gui


@immapp.static(gui=None)
def demo_launch():
    statics = demo_launch
    if statics.gui is None:
        statics.gui = make_gui()
    statics.gui()


def main():
    gui = make_gui()
    immapp.run(gui, with_tex_inspect=True, with_markdown=True, window_size=(1200, 1000))


if __name__ == "__main__":
    main()
