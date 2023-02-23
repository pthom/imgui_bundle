# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import imgui, imgui_md, immapp, ImVec2
from imgui_bundle.demos_python import demo_utils  # this will set the assets folder


def demo_gui():
    imgui_md.render_unindented(
        """
        # Dear ImGui demo
         [Dear ImGui](https://github.com/ocornut/imgui.git) is one possible implementation of an idea generally described as the IMGUI (Immediate Mode GUI) paradigm. 
         
         The following is the output of imgui.show_demo_window(), which is always accessible online with [ImGui Manual](https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html). 
    """
    )
    imgui.show_demo_window()
    demo_utils.animate_logo(
        "images/logo_imgui_600.png", 2.0, ImVec2(1.0, 4.8), 0.45, "https://github.com/ocornut/imgui"
    )


if __name__ == "__main__":
    immapp.run(gui_function=demo_gui, with_markdown=True, window_size=(800, 600))  # type: ignore
