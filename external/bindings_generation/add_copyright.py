# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from typing import Dict
import os
from bindings_generation import paths


copyright_str = "Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle"


directories = """
./cmake
./tests
./pybind_native_debug
./ci_scripts
./lg_cmake_utils
./external
./external/hello_imgui
./external/hello_imgui/bindings
./external/imgui_md
./external/imgui_md/imgui_md_wrapper
./external/imgui_md/bindings
./external/ImGuizmo
./external/ImGuizmo/ImGuizmoPure
./external/ImGuizmo/bindings
./external/implot
./external/implot/bindings
./external/imgui_toggle
./external/imgui_toggle/bindings
./external/immvision
./external/immvision/bindings
./external/imgui-node-editor
./external/imgui-node-editor/external
./external/imgui-node-editor/bindings
./external/imgui-node-editor/imgui_node_editor_immapp
./external/imgui
./external/imgui/bindings
./external/bindings_generation
./external/bindings_generation/cpp
./external/imspinner
./external/imspinner/bindings
./external/_sandbox
./external/_sandbox/imfiledialog_test
./external/_sandbox/imguizmo_test
./external/immapp
./external/immapp/bindings
./external/portable_file_dialogs
./external/portable_file_dialogs/bindings
./external/ImFileDialog
./external/ImFileDialog/bindings
./external/ImFileDialog/bundle_integration
./external/imgui-command-palette
./external/imgui-command-palette/bindings
./external/imgui-command-palette/imgui-command-palette-py-wrapper
./external/imgui-knobs
./external/imgui-knobs/bindings
./external/imgui_tex_inspect
./external/imgui_tex_inspect/bindings
./external/ImGuiColorTextEdit
./external/ImGuiColorTextEdit/bindings
./bindings/imgui_bundle
./bindings/imgui_bundle/demos_cpp
./bindings/imgui_bundle/demos_assets
./bindings/imgui_bundle/imgui
./bindings/imgui_bundle/immapp
./bindings/imgui_bundle/doc
./bindings/imgui_bundle/assets
./bindings/imgui_bundle/demos_python
./imgui_bundle_cmake
./_example_integration
./src
./src/imgui_bundle
""".splitlines(
    keepends=False
)


extensions = set()

extensionCommentMarkers: Dict[str, str] = {
    # "pyi": "#",
    "py": "#",
    # "cpp": "//",
    # "h": "//",
    # "cmake": "#",
    # "txt": "#",
}


def add_copyright(filename):
    extension = file.split(".")[-1]
    if extension in extensionCommentMarkers.keys():
        comment_marker = extensionCommentMarkers[extension]
        copyright_comment = comment_marker + " " + copyright_str

        with open(filename, "r", encoding="utf8") as f:
            content = f.read()
            lines = content.split("\n")

        if lines[0] != copyright_comment:
            lines = [copyright_comment] + lines
            content_with_copyright = "\n".join(lines)
            with open(filename, "w", encoding="utf8") as f:
                f.write(content_with_copyright)


for directory in directories:
    full_dir_path = paths.repo_dir() + "/" + directory
    for file in os.listdir(full_dir_path):
        full_file_path = full_dir_path + "/" + file
        if os.path.isfile(full_file_path):
            add_copyright(full_file_path)
