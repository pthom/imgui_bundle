# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle

from imgui_bundle import imgui, hello_imgui, imgui_md, immapp, ImVec2
from imgui_bundle.demos_python import demo_utils  # this will set the assets folder


def _do_spawn_demo(demo_name: str):
    import os.path
    import subprocess
    import sys
    this_dir = os.path.dirname(__file__)
    demo_file = this_dir + "/demos_nanovg/" + demo_name + ".py"
    subprocess.Popen([sys.executable, demo_file])


def demo_gui():
    static = demo_gui
    if not hasattr(static, "is_full_demo_opened"):
        static.is_full_demo_opened = False
    if not hasattr(static, "is_simple_demo_opened"):
        static.is_simple_demo_opened = False
    if not hasattr(static, "show_full_demo_rendering_code"):
        static.show_full_demo_rendering_code = False

    imgui_md.render_unindented("""
        # NanoVG
        [NanoVG](https://github.com/memononen/nanovg) Antialiased 2D vector drawing library on top of OpenGL for UI and visualizations.
        """)

    if not static.is_full_demo_opened and not static.is_simple_demo_opened:
        imgui.same_line(imgui.get_window_width() - hello_imgui.em_size(14.0))
        if hello_imgui.image_button_from_asset("images/nanovg_full_demo.jpg", ImVec2(hello_imgui.em_size(11.0), 0.0)):
            _do_spawn_demo("demo_nanovg_full")

    nb_code_lines = 35

    if imgui.collapsing_header("Full Demo"):
        static.is_full_demo_opened = True
        imgui.begin_group()
        imgui.text(
            "This is the original NanoVG demo, integrated to ImGui Bundle (and also ported to python).\n"
            "Click the button below to launch the demo"
        )
        imgui.new_line()
        if imgui.button("Run full demo"):
            _do_spawn_demo("demo_nanovg_full")
        imgui.end_group()

        imgui.same_line(imgui.get_window_width() - hello_imgui.em_size(14.0))
        if hello_imgui.image_button_from_asset("images/nanovg_full_demo.jpg", ImVec2(hello_imgui.em_size(11.0), 0.0)):
            _do_spawn_demo("demo_nanovg_full")

        if imgui.radio_button("Show launcher code", not static.show_full_demo_rendering_code):
            static.show_full_demo_rendering_code = False
        imgui.same_line()
        if imgui.radio_button("Show rendering code", static.show_full_demo_rendering_code):
            static.show_full_demo_rendering_code = True

        if not static.show_full_demo_rendering_code:
            demo_utils.show_python_vs_cpp_file("demos_nanovg/demo_nanovg_full", nb_code_lines)
        else:
            demo_utils.show_python_vs_cpp_file("demos_nanovg/demo_nanovg_full/demo_nanovg_full_impl", nb_code_lines)
    else:
        static.is_full_demo_opened = False

    if imgui.collapsing_header("Simple Demo"):
        static.is_simple_demo_opened = True
        imgui.begin_group()
        imgui.text(
            "This is a simpler demo, that shows how to display NanoVG as the background, or as a texture.\n"
            "(via a framebuffer object)\n"
            "Click the button below to launch the demo"
        )
        imgui.new_line()
        if imgui.button("Run simple demo"):
            _do_spawn_demo("demo_nanovg_heart")
        imgui.end_group()
        imgui.same_line(imgui.get_window_width() - hello_imgui.em_size(14.0))
        if hello_imgui.image_button_from_asset("images/nanovg_demo_heart.jpg", ImVec2(hello_imgui.em_size(11.0), 0.0)):
            _do_spawn_demo("demo_nanovg_heart")
        demo_utils.show_python_vs_cpp_file("demos_nanovg/demo_nanovg_heart", nb_code_lines)
    else:
        static.is_simple_demo_opened = False


if __name__ == "__main__":
    immapp.run(demo_gui, window_size=(1000, 800), with_markdown=True, with_node_editor=True)
