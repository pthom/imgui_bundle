# Demo imgui_tex_inspect
# See equivalent C++ program: demos_cpp/demos_tex_inspect/demo_tex_inspect.main.cpp
from imgui_bundle import imgui_tex_inspect, hello_imgui, imgui, immapp, ImVec2
from imgui_bundle.demos.demo_utils.api_demos import *


hello_imgui.set_assets_folder(demos_assets_folder())


# This returns a closure function that will later be invoked to run the app
def make_closure_demo_tex_inspect() -> GuiFunction:
    texture_id = None
    texture_size = ImVec2(512.0, 512.0)
    showDemoImGuiTexInspect = False

    def gui():
        nonlocal texture_id, showDemoImGuiTexInspect
        if texture_id is None:
            texture_id = hello_imgui.im_texture_id_from_asset("images/bear_transparent.png")

        _, showDemoImGuiTexInspect = imgui.checkbox("Show ImGuiTexInspect::ShowDemoWindow()", showDemoImGuiTexInspect)
        if showDemoImGuiTexInspect:
            imgui_tex_inspect.show_demo_window()

        imgui.separator()

        # Simple demo

        imgui.text("Simple Demo")
        flags = 0
        inspectorSize = imgui_tex_inspect.SizeIncludingBorder(ImVec2(600, 600))
        if imgui_tex_inspect.begin_inspector_panel("Texture Inspector", texture_id, texture_size, flags, inspectorSize):
            imgui_tex_inspect.end_inspector_panel()

    return gui


def main():
    gui = make_closure_demo_tex_inspect()
    immapp.run(gui, with_tex_inspect=True, window_size=(1000, 1000))


if __name__ == "__main__":
    main()
