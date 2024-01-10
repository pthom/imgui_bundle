# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from typing import List
from bindings_generation.external_library import ExternalLibrary


# fmt: off

def lib_glfw() -> ExternalLibrary:
    return ExternalLibrary(
        name="glfw",
        official_git_url="https://github.com/glfw/glfw.git",
        official_branch="3.3-stable",
        is_published_in_python=False
    )


def lib_hello_imgui() -> ExternalLibrary:
    return ExternalLibrary(
        name="hello_imgui",
        official_git_url="https://github.com/pthom/hello_imgui.git",
        official_branch="master"
    )


def lib_im_file_dialog() -> ExternalLibrary:
    return ExternalLibrary(
        name="ImFileDialog",
        official_git_url="https://github.com/dfranx/ImFileDialog.git",
        official_branch="main",
        fork_git_url="https://github.com/pthom/ImFileDialog.git",
    )


def lib_imcoolbar() -> ExternalLibrary:
    return ExternalLibrary(
        name="ImCoolBar",
        official_git_url="https://github.com/aiekick/ImCoolBar.git",
        official_branch="master",
        fork_git_url="https://github.com/pthom/ImCoolBar.git",
        fork_branch="imgui_bundle"
    )


def lib_imgui() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui",
        official_git_url="https://github.com/ocornut/imgui.git",
        official_branch="docking",
        fork_git_url="https://github.com/pthom/imgui.git"
    )


def lib_imgui_test_engine() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui_test_engine",
        official_git_url="https://github.com/ocornut/imgui_test_engine.git",
        official_branch="main",
        fork_git_url="https://github.com/pthom/imgui_test_engine.git",
        is_published_in_python=False  # published by generate_imgui.py
    )


def lib_imgui_command_palette() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui-command-palette",
        official_git_url="https://github.com/hnOsmium0001/imgui-command-palette.git",
        official_branch="master",
        fork_git_url="https://github.com/pthom/imgui-command-palette.git"
    )


def lib_imgui_knobs() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui-knobs",
        official_git_url="https://github.com/altschuler/imgui-knobs",
        official_branch="main",
        fork_git_url="https://github.com/pthom/imgui-knobs.git",
    )


def lib_imgui_node_editor() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui-node-editor",
        official_git_url="https://github.com/thedmd/imgui-node-editor.git",
        official_branch="develop",
        fork_git_url="https://github.com/pthom/imgui-node-editor.git",
    )


def lib_imgui_md() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui_md",
        official_git_url="https://github.com/mekhontsev/imgui_md",
        official_branch="main",
        fork_git_url="https://github.com/pthom/imgui_md.git",
    )


def lib_md4c() -> ExternalLibrary:
    return ExternalLibrary(
        name="md4c",
        official_git_url="https://github.com/mity/md4c",
        official_branch="master",
        custom_git_folder="imgui_md/md4c",
        is_sub_library=True,
        is_published_in_python=False
    )


def lib_imgui_tex_inspect() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui_tex_inspect",
        official_git_url="https://github.com/andyborrell/imgui_tex_inspect.git",
        official_branch="main",
        fork_git_url="https://github.com/pthom/imgui_tex_inspect.git",
    )


def lib_imgui_toggle() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui_toggle",
        official_git_url="https://github.com/cmdwtf/imgui_toggle.git",
        official_branch="main",
        fork_git_url="https://github.com/pthom/imgui_toggle.git"
    )


def lib_imgui_color_text_edit() -> ExternalLibrary:
    return ExternalLibrary(
        name="ImGuiColorTextEdit",
        official_git_url="https://github.com/BalazsJako/ImGuiColorTextEdit.git",
        official_branch="dev",
        fork_git_url="https://github.com/pthom/ImGuiColorTextEdit.git",
    )


def lib_imguizmo() -> ExternalLibrary:
    return ExternalLibrary(
        name="ImGuizmo",
        official_git_url="https://github.com/CedricGuillemet/ImGuizmo.git",
        official_branch="master",
        fork_git_url="https://github.com/pthom/ImGuizmo.git",
    )


def lib_immapp() -> ExternalLibrary:
    return ExternalLibrary(
        # this is an internal library, it does not have a git url
        name="immapp"
    )


def lib_immvision() -> ExternalLibrary:
    return ExternalLibrary(
        name="immvision",
        official_git_url="https://github.com/pthom/immvision.git",
        official_branch="master"
    )


def lib_cvnp() -> ExternalLibrary:
    return ExternalLibrary(
        name="cvnp",
        official_git_url="https://github.com/pthom/cvnp.git",
        official_branch="master",
        custom_git_folder="immvision/cvnp",
        is_sub_library=True,
        is_published_in_python=False
    )


def lib_implot() -> ExternalLibrary:
    return ExternalLibrary(
        name="implot",
        official_git_url="https://github.com/epezent/implot.git",
        official_branch="master"
    )


def lib_imspinner() -> ExternalLibrary:
    # We use a copy of the library source for the moment, instead of a fork
    return ExternalLibrary(
        name="imspinner",
        # official_git_url="https://github.com/dalerank/imspinner.git",
        #official_branch="master"
    )


def lib_portable_file_dialogs() -> ExternalLibrary:
    # this header only library is present inside immvision
    # its header file is taken from there
    return ExternalLibrary(
        name="portable_file_dialogs"
    )


def lib_nanovg() -> ExternalLibrary:
    return ExternalLibrary(
        name="nanovg",
        official_git_url="https://github.com/memononen/nanovg.git",
        official_branch="master",
        fork_git_url="https://github.com/pthom/nanovg.git",
        fork_branch="imgui_bundle"
    )


# fmt: on


ALL_LIBS = [
    lib_imgui(),  # must be first as it declare bindings used by the next ones
    lib_imgui_test_engine(),
    lib_glfw(),
    lib_hello_imgui(),
    lib_imcoolbar(),
    lib_im_file_dialog(),
    lib_imgui_command_palette(),
    lib_imgui_knobs(),
    lib_imgui_node_editor(),
    lib_imgui_md(),
    lib_md4c(),
    lib_imgui_tex_inspect(),
    lib_imgui_toggle(),
    lib_imgui_color_text_edit(),
    lib_imguizmo(),
    lib_immapp(),
    lib_immvision(),
    lib_cvnp(),
    lib_implot(),
    lib_imspinner(),
    lib_portable_file_dialogs(),
    lib_nanovg(),
]


def published_libs() -> List[ExternalLibrary]:
    r = list(filter(lambda lib: lib.is_published_in_python, ALL_LIBS))
    return r


def reattach_all_submodules():
    """
    Will remove existing git remotes
    Then add two remotes if it is a fork
        - official : points to the official repo
        - pthom: points to the forked library
    Or add one remote if it is not a fork
        - official : points to the official repo
    then attach the submodule to the correct remote branch (set-upstream)
    """
    for lib in ALL_LIBS:
        if lib.is_submodule():
            print(lib.name)
            lib.run_reattach_submodule()


def pull_all_submodules():
    for lib in ALL_LIBS:
        if lib.is_submodule():
            print(lib.name)
            lib.run_pull()


def fetch_all_submodules():
    for lib in ALL_LIBS:
        if lib.is_submodule():
            print(lib.name)
            lib.cmd_fetch_all().run()
