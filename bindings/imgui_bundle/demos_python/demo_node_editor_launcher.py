import os.path
import subprocess
import sys
from imgui_bundle import imgui, hello_imgui, immapp
from imgui_bundle.demos_python import demo_utils, demos_node_editor


def make_gui() -> demo_utils.GuiFunction:
    def gui():
        demo_utils.render_md_unindented(
            """
        # imgui-node-editor
        [imgui-node-editor](https://github.com/thedmd/imgui-node-editor) is a zoomable and node Editor built using Dear ImGui.

        Open the demos below by clicking on their title.
        """
        )

        if imgui.collapsing_header("Screenshot - BluePrint"):
            demo_utils.render_md_unindented("This is a screenshot showing the possibilities of the node editor")
            hello_imgui.image_from_asset("images/node_editor_screenshot.jpg", immapp.em_to_vec2(40, 0))
        if imgui.collapsing_header("Screenshot - Image editing"):
            demo_utils.render_md_unindented(
                "This is another screenshot showing the possibilities of the node editor, when combined with immvision")
            hello_imgui.image_from_asset("images/node_editor_fiat.jpg", immapp.em_to_vec2(60, 0))
        if imgui.collapsing_header("demo basic interaction"):
            demos_node_editor.demo_node_editor_basic.demo_launch()
            demo_utils.show_python_vs_cpp_file("demos_node_editor/demo_node_editor_basic", nb_lines=30)

    return gui


@immapp.static(gui=None)
def demo_launch():
    statics = demo_launch
    if statics.gui is None:
        statics.gui = make_gui()
    statics.gui()


def main():
    gui = make_gui()
    immapp.run(gui, window_size=(1000, 800), with_markdown=True)


if __name__ == "__main__":
    main()
