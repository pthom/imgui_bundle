# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import imgui, imgui_md, immapp, ImVec2
from imgui_bundle.demos_python import demo_utils  # this will set the assets folder

try:
    from imgui_bundle import imgui_manual
    _has_imgui_manual = True
except ImportError:
    _has_imgui_manual = False


def demo_gui():
    imgui_md.render_unindented(
        """
        # Dear ImGui demo
        Browse the demos below, and look at their code in the right panel! You may switch between C++ and Python code with the toggle at the top right of this window.
    """
    )

    imgui.new_line()
    imgui.separator()

    if _has_imgui_manual:
        imgui_manual.show_imgui_manual_gui(
            imgui_manual.ImGuiManualLibrary.imgui, imgui_manual.ImGuiManualCppOrPython.python, False
        )
    else:
        imgui.show_demo_window()

    demo_utils.animate_logo(
        "images/logo_imgui_600.jpg",
        2.0,
        ImVec2(1.0 * 0.64, 4.8 * 0.64),
        0.45,
        "https://github.com/ocornut/imgui",
    )


if __name__ == "__main__":
    immapp.run(gui_function=demo_gui, with_markdown=True, window_size=(800, 600))  # type: ignore
