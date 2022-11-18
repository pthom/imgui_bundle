import subprocess
import sys
import os

from imgui_bundle import imgui_color_text_edit as text_edit, imgui_md
from imgui_bundle import imgui, ImVec2


EDITOR = text_edit.TextEditor()
EDITOR.set_text("")


def python_path():
    executable = os.path.realpath(sys.executable)
    return executable


def show_one_feature(demo_file):
    if imgui.button(demo_file):
        this_dir = os.path.dirname(__file__)
        demo_file_path = this_dir + "/" + demo_file

        with open(demo_file_path) as f:
            code = f.read()
        EDITOR.set_text(code)
        subprocess.Popen([sys.executable, demo_file_path])


def demo_imgui():
    imgui_md.render(
        """
# ImGui example application
imgui_example_glfw_opengl3.py is a direct adaptation of an example from Dear ImGui: 
[imgui/examples/example_glfw_opengl3/main.cpp](https://github.com/ocornut/imgui/blob/master/examples/example_glfw_opengl3/main.cpp)

You can configure and run imgui, opengl and glfw (or sdl, etc.) manually as show in this example.
""")
    show_one_feature("imgui_example_glfw_opengl3.py")


def demo_hello_imgui():
    from imgui_bundle import imgui

    imgui_md.render(
        """
# HelloImGui
[HelloImGui](https://github.com/pthom/hello_imgui) is a wrapper around ImGui that enables to easily create applications with ImGui.
* Hello ImGui [API Doc](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md)
* Docking layout [specific documentation](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md#docking)
    """
    )

    imgui.begin_group()

    imgui.text("Hello world demo: how to start an app in as few lines as possible")
    show_one_feature("demos_hello_imgui/demo_hello_world.py")

    imgui.text("How to load assets")
    show_one_feature("demos_hello_imgui/demo_assets.py")

    imgui.text_wrapped(
        """How to build complex applications layouts, with dockable panels, 
that can even become independent windows. 
How to customize the theme."""
    )
    show_one_feature("demos_hello_imgui/demo_docking.py")

    imgui.end_group()
    imgui.same_line(0, 30)
    imgui.begin_group()

    imgui.text("How to quickly run an app that uses implot and/or markdown")
    show_one_feature("demos_hello_imgui/demo_implot_markdown.py")

    imgui.text("How to have smooth animations")
    show_one_feature("demos_hello_imgui/demo_powersave.py")

    imgui.text("Animated heart")
    show_one_feature("haikus/haiku_implot_heart.py")

    imgui.end_group()


def demo_apps():
    imgui.begin_child("##Doc", ImVec2(0, imgui.get_window_height() - 300))
    demo_imgui()
    demo_hello_imgui()
    imgui.end_child()

    if len(EDITOR.get_text()) > 1:
        imgui.separator()
        imgui.text("Code for this demo")
        EDITOR.render("Code")


if __name__ == "__main__":
    from imgui_bundle import run

    run(demo_apps, with_markdown=True, window_size=(800, 800))
