import os.path
import subprocess
import sys
from imgui_bundle import immapp, imgui
from imgui_bundle.demos import demo_utils, demos_tex_inspect


def make_gui() -> demo_utils.GuiFunction:
    def gui():
        demo_utils.render_md_unindented("""
        [imgui_tex_inspect](https://github.com/andyborrell/imgui_tex_inspect) is a texture inspector tool for Dear ImGui
        ImGuiTexInspect is a texture inspector tool for Dear ImGui. It's a debug tool that allows you to easily inspect the data in any texture.

        Whereas *imgui_tex_inspect* is dedicated to texture analysis, *immvision* is more dedicated to image processing and computer vision.

        Open the demos below by clicking on their title.
        """)

        if imgui.collapsing_header("Simple Demo"):
            demos_tex_inspect.demo_tex_inspect_simple.demo_launch()
            demo_utils.show_python_vs_cpp_file("demos_tex_inspect/demo_tex_inspect_simple")
        if imgui.collapsing_header("Full Demo"):
            imgui.text("Click the button below to launch the demo")
            if imgui.button("Run demo"):
                this_dir = os.path.dirname(__file__)
                subprocess.Popen([sys.executable, this_dir + "/demos_tex_inspect/demo_tex_inspect_demo_window.py"])
            demo_utils.show_python_vs_cpp_file("demos_tex_inspect/demo_tex_inspect_demo_window")
    return gui


@immapp.static(gui=None)
def demo_launch():
    statics = demo_launch
    if statics.gui is None:
        statics.gui = make_gui()
    statics.gui()
    

def main():
    gui = make_gui()
    immapp.run(gui, window_size=(1000, 800), with_markdown=True, with_tex_inspect=True)


if __name__ == "__main__":
    main()
