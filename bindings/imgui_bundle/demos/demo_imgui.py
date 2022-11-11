from imgui_bundle import imgui, imgui_md, static, ImVec2
from imgui_bundle.demos import code_str_utils
import inspect


def md_render_unindent(md: str):
    u = code_str_utils.unindent_code(md, flag_strip_empty_lines=True, is_markdown=True)
    imgui_md.render(u)


@static(is_initialized=False)
def demo_imgui():
    static = demo_imgui

    md_render_unindent(
        """
        # Dear ImGui demo
         [Dear ImGui](https://github.com/ocornut/imgui.git) is one possible implementation of an idea generally described as the IMGUI (Immediate Mode GUI) paradigm. 
         
         The following is the output of imgui.show_demo_window(), which is always accessible online with [ImGui Manual](https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html). 
    """
    )
    imgui.show_demo_window()


if __name__ == "__main__":
    from imgui_bundle import run

    run(gui_function=demo_imgui, with_markdown=True, window_size=(800, 600))
