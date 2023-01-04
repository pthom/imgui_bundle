from imgui_bundle import imgui, imgui_md, immapp


def demo_gui():
    imgui_md.render_unindented(
        """
        # Dear ImGui demo
         [Dear ImGui](https://github.com/ocornut/imgui.git) is one possible implementation of an idea generally described as the IMGUI (Immediate Mode GUI) paradigm. 
         
         The following is the output of imgui.show_demo_window(), which is always accessible online with [ImGui Manual](https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html). 
    """
    )
    imgui.show_demo_window()


if __name__ == "__main__":
    immapp.run(gui_function=demo_gui, with_markdown=True, window_size=(800, 600))  # type: ignore
