import os
import shutil


LG_PROJECTS_DIR = os.path.realpath(os.path.dirname(__file__) + "/../..")


def copy_imgui_bindings():
    """
    We want to copy the following files:
    bindings/
    ├── imgui_boxed_types.h
    ├── imgui_docking_internal_types.h
    ├── lg_imgui/
    │         ├── imgui.pyi                This file need to go to bindings/lg_imgui_bundle
    └── pybind_imgui.cpp

    from lg_imgui to the different lg_imgui_bundle
    """

    child_library = "lg_imgui_bundle"
    src_folder = f"{LG_PROJECTS_DIR}/lg_imgui/bindings"
    dst_folder = f"{LG_PROJECTS_DIR}/{child_library}/bindings"

    files_to_copy = [
        "imgui_boxed_types.h",
        "imgui_docking_internal_types.h",
        "pybind_imgui.cpp",
    ]
    for file_to_copy in files_to_copy:
        src_file = f"{src_folder}/{file_to_copy}"
        dst_file = f"{dst_folder}/{file_to_copy}"
        shutil.copy(src_file, dst_file)

    # Handle "lg_imgui/imgui.pyi",
    src_file = f"{src_folder}/lg_imgui/imgui.pyi"
    dst_file = f"{dst_folder}/{child_library}/imgui.pyi"
    shutil.copy(src_file, dst_file)



if __name__ == "__main__":
    copy_imgui_bindings()
