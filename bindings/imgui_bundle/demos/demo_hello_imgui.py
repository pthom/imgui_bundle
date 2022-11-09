import subprocess
import sys
import os

from imgui_bundle import static
from imgui_bundle import imgui_color_text_edit as text_edit, imgui_md
from imgui_bundle import ImVec2


def python_path():
    executable = os.path.realpath(sys.executable)
    return executable


@static(was_inited=False)
def demo_hello_imgui():
    static = demo_hello_imgui
    if not static.was_inited:
        static.editor = text_edit.TextEditor()
        static.editor.set_text("")
        static.was_inited = True
    editor = static.editor

    from imgui_bundle import imgui

    imgui_md.render(
        """
# HelloImGui
[HelloImGui](https://github.com/pthom/hello_imgui) is a wrapper around ImGui that enables to easily create applications with ImGui.

Features
* Easy setup
* Advanced docking support with easy layout
    """
    )

    def show_one_feature(demo_file):
        if imgui.button(demo_file):
            this_dir = os.path.dirname(__file__)
            demo_file_path = this_dir + "/" + demo_file

            with open(demo_file_path) as f:
                code = f.read()
            editor.set_text(code)
            subprocess.Popen([sys.executable, demo_file_path])

    imgui.text("Click on any button to launch a demo, and see its code")
    imgui.new_line()

    imgui.text("Hello world demo: how to start an app in as few lines as possible")
    show_one_feature("demos_hello_imgui/demo_hello_world.py")

    imgui.text("How to load assets")
    show_one_feature("demos_hello_imgui/demo_assets.py")

    imgui.text(
        "How to build complex applications layouts, with dockable panels, that can even become independent windows"
    )
    show_one_feature("demos_hello_imgui/demo_docking.py")

    imgui.text("How to quickly run an app that uses implot and/or markdown")
    show_one_feature("demos_hello_imgui/demo_implot_markdown.py")

    imgui.text("How to have smooth animations")
    show_one_feature("demos_hello_imgui/demo_powersave.py")

    imgui.text("Animated heart")
    show_one_feature("haikus/haiku_implot_heart.py")

    imgui.new_line()
    imgui_md.render(
        """
* Hello ImGui [API Doc](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md)
* Docking layout [specific documentation](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md#docking)
    """
    )

    if len(editor.get_text()) > 1:
        imgui.separator()
        imgui.text("Code for this demo")
        editor.render("Code")


if __name__ == "__main__":
    from imgui_bundle import run

    run(demo_hello_imgui, with_markdown=True, window_size=(800, 800))
