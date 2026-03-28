# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import imgui, imgui_md, immapp

from imgui_bundle.demos_python.demo_utils.imgui_explorer_setup import get_imgui_explorer, get_package_path
imgui_explorer, _has_imgui_explorer = get_imgui_explorer()


def demo_gui():
    imgui_md.render_unindented(
        """
        # ImAnim
        ImAnim is an Animation Engine for Dear ImGui. Browse the demos below, and look at their code in the right panel! You may switch between C++ and Python code with the toggle at the top right of this window.
    """
    )

    imgui.new_line()
    imgui.separator()

    if _has_imgui_explorer:
        imgui_explorer.show_imgui_explorer_gui_python(
            imgui_explorer.ImGuiExplorerLibrary.im_anim, get_package_path()
        )
    else:
        imgui.text("Demo unavailable, because Dear ImGui Manual library is not included in this build.")


if __name__ == "__main__":
    immapp.run(gui_function=demo_gui, with_markdown=True, window_size=(1000, 800))  # type: ignore
