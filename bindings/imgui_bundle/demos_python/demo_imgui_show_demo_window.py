from imgui_bundle import imgui, imgui_md, immapp
from imgui_bundle.immapp import static


@static(is_initialized=False)
def show_demo_window():
    static = show_demo_window

    imgui_md.render_unindented(
        """
        # Dear ImGui demo
         [Dear ImGui](https://github.com/ocornut/imgui.git) is one possible implementation of an idea generally described as the IMGUI (Immediate Mode GUI) paradigm. 
         
         The following is the output of imgui.show_demo_window(), which is always accessible online with [ImGui Manual](https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html). 
    """
    )
    imgui.show_demo_window()


if __name__ == "__main__":
    from imgui_bundle import immapp

    immapp.run(gui_function=show_demo_window, with_markdown=True, window_size=(800, 600))  # type: ignore
