# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import imgui, imgui_md, immapp, ImVec2, register_demos_assets_folder
from imgui_bundle.demos_python import demo_utils
from imgui_bundle.demos_python.demo_utils.imgui_explorer_setup import get_imgui_explorer, get_package_path

register_demos_assets_folder()
imgui_explorer, _has_imgui_explorer = get_imgui_explorer()


def demo_gui():
    imgui_md.render_unindented(
        """
        # Dear ImGui
        Browse the demos below, and look at their code in the right panel!
    """
    )

    imgui.new_line()
    imgui.separator()

    if _has_imgui_explorer:
        imgui_explorer.show_imgui_explorer_gui_python(
            imgui_explorer.ImGuiExplorerLibrary.imgui, get_package_path()
        )
    else:
        imgui.show_demo_window()

    demo_utils.animate_logo(
        "images/logo_imgui_600.jpg",
        2.0,
        ImVec2(1.0 * 0.2, 4.8 * 0.2),
        0.45,
        "https://github.com/ocornut/imgui",
    )


if __name__ == "__main__":
    immapp.run(gui_function=demo_gui, with_markdown=True, window_size=(800, 600))  # type: ignore
