# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

from imgui_bundle import imgui_md
from imgui_bundle import immapp
from imgui_bundle.demos_python.demo_utils.api_demos import GuiFunction
from imgui_bundle.demos_python.demo_utils.demo_app_table import DemoAppTable, DemoApp


DOC = """
# HelloImGui and ImmApp

* [HelloImGui](https://pthom.github.io/hello_imgui) is a library based on ImGui that enables to easily create applications with ImGui.
* [ImApp](https://github.com/pthom/imgui_bundle/blob/main/external/immapp/immapp/runner.h) (aka "Immediate App", a submodule of ImGuiBundle) is a thin extension of HelloImGui that enables to easily initialize the ImGuiBundle addons that require additional setup at startup.

## Demo applications (*scroll with the mouse wheel below for more demos*)
    """


# This returns a closure function that will later be invoked to run the app
def make_gui() -> GuiFunction:
    demo_apps = [
        DemoApp(
            "demo_hello_world",
            "Hello world demo: how to create an app with ImmApp in a few lines.",
        ),
        DemoApp(
            "demo_assets_addons",
            "How to use assets, and how to use add-ons (Markdown and ImPlot)",
        ),
        DemoApp(
            "demo_docking",
            "Full Demo: complex docking layout, additional fonts (including colored fonts and emojis), log window, status bar, user settings, etc."
        ),
        DemoApp("demo_custom_background", "How to use a custom 3D background"),
        DemoApp(
            "demo_powersave",
            "How to have smooth animations, and how spare the CPU when idling",
        ),
        DemoApp(
            "demo_font_common_glyph_range",
            "How to load fonts with specific glyph ranges (e.g., Chinese, Japanese, Korean)",
        ),
        DemoApp(
            "demo_testengine",
            "How to use ImGui Test Engine to test and automate your application",
        ),
        DemoApp("demo_python_context_manager",
                "How to use a python context manager for `imgui.begin()`, `imgui.end()`, etc."),
        DemoApp(
            "demo_command_palette",
            "a Sublime Text or VSCode style command palette in ImGui",
        ),
        DemoApp(
            "demo_parametric_curve",
            "Illustration of the Immediate GUI paradigm, with a simple parametric curve",
        ),
        DemoApp("haiku_implot_heart", "Share some love for ImGui and ImPlot"),
        DemoApp("demo_drag_and_drop", "Drag and drop demo"),
        DemoApp(
            "demo_implot_markdown",
            "How to quickly run an app that uses implot and/or markdown with ImmApp",
        ),
        DemoApp(
            "demo_matplotlib",
            "Python: display matplotlib figures in an ImGui window (animated or static)",
        ),
        DemoApp(
            "demo_pydantic",
            "Python: How to use ImVec2 and ImVec4 with Pydantic",
        ),
        DemoApp(
            "imgui_example_glfw_opengl3",
            "Python: translation of the [GLFW+OpenGL3 example](https://github.com/ocornut/imgui/blob/master/examples/example_glfw_opengl3/main.cpp) from Dear ImGui. "
            "Demonstrates how to port from C++ to Python (here, *backend rendering is implemented in C++*)",
        ),
        DemoApp(
            "example_python_backend_glfw3",
            "Python: how to use ImGui with GLFW3 using a *full python* backend",
            is_python_backend_demo=True,
        ),
        DemoApp(
            "example_python_backend_sdl2",
            "Python: how to use ImGui with SDL using a *full python* backend",
            is_python_backend_demo=True,
        ),
        DemoApp(
            "example_python_backend_pyglet",
            "Python: how to use ImGui with pyglet using a *full python* backend",
            is_python_backend_demo=True,
        ),
    ]

    this_dir = os.path.dirname(__file__)
    demo_python_folder = this_dir + "/demos_immapp"
    demo_cpp_folder = os.path.abspath(
        demo_python_folder + "/../../demos_cpp/demos_immapp"

    )
    demo_python_backend_folder = os.path.abspath(
        demo_python_folder + "/../../python_backends/examples"
    )
    demo_app_table = DemoAppTable(demo_apps, demo_python_folder, demo_cpp_folder, demo_python_backend_folder)

    def gui():
        nonlocal demo_apps
        imgui_md.render(DOC)
        demo_app_table.gui()

    return gui


@immapp.static(gui=None)
def demo_gui():
    static = demo_gui
    if static.gui is None:
        static.gui = make_gui()
    static.gui()


def main():
    immapp.run(demo_gui, with_markdown=True, window_size=(1000, 800))  # type: ignore


if __name__ == "__main__":
    main()
