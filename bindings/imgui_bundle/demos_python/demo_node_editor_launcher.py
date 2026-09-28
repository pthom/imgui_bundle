# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import imgui, immapp, rich_md
from imgui_bundle.demos_python import demo_utils  # this will set the assets folder
from imgui_bundle.demos_python import demos_node_editor


def demo_gui():
    rich_md.render(
        """
    # imgui-node-editor
    [imgui-node-editor](https://github.com/thedmd/imgui-node-editor) is a zoomable and node Editor built using Dear ImGui.

    Open the demos below by clicking on their title.
    """
    )

    if imgui.collapsing_header("demo basic interaction"):
        demos_node_editor.demo_node_editor_basic.demo_gui()
        demo_utils.show_python_vs_cpp_file(
            "demos_node_editor/demo_node_editor_basic", nb_lines=30
        )
    if imgui.collapsing_header("haiku - Romeo and Juliet"):
        demos_node_editor.demo_romeo_and_juliet.demo_gui()
        demo_utils.show_python_vs_cpp_file(
            "demos_node_editor/demo_romeo_and_juliet", nb_lines=30
        )


def main():
    immapp.run(
        demo_gui, window_size=(1000, 800), with_markdown=True, with_node_editor=True
    )


if __name__ == "__main__":
    main()
