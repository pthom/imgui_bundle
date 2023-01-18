# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

from imgui_bundle import imgui_md
from imgui_bundle import immapp
from imgui_bundle.demos_python.demo_utils.api_demos import GuiFunction
from imgui_bundle.demos_python.demo_utils.demo_app_table import DemoAppTable, DemoApp


DOC = """
# HelloImGui and ImmApp

* [HelloImGui](https://github.com/pthom/hello_imgui) is a library based on ImGui that enables to easily create applications with ImGui.
  Link to the [API documentation](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md). Docking layout [documentation](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md#docking)
* [ImApp](https://github.com/pthom/imgui_bundle/blob/dev/bindings/imgui_bundle/immapp/immapp_cpp.pyi) (aka "Immediate App", a submodule of ImGuiBundle) is a thin extension of HelloImGui that enables to easily initialize the ImGuiBundle addons that require additional setup at startup. 

## Demo applications
    """


# This returns a closure function that will later be invoked to run the app
def make_gui() -> GuiFunction:
    demo_apps = [
        DemoApp("demo_hello_world", "Hello world demo: how to start an app with ImmApp in as few lines as possible"),
        DemoApp("demo_assets", "How to load assets with HelloImGui"),
        DemoApp(
            "demo_docking",
            """How to build complex applications layouts, with dockable panels,that can even become independent windows. How to customize the theme.""",
        ),
        DemoApp("demo_implot_markdown", "How to quickly run an app that uses implot and/or markdown with ImmApp"),
        DemoApp(
            "demo_powersave", "How to have smooth animations, and how to let the application save CPU when idle"
        ),
        DemoApp("demo_custom_font", "How to load custom fonts"),
        DemoApp("demo_command_palette", "a Sublime Text or VSCode style command palette in ImGui"),
        DemoApp("haiku_implot_heart", "Share some love for ImGui and ImPlot"),
        DemoApp(
            "imgui_example_glfw_opengl3",
            """
            How to port an existing ImGui application to python<br>
            imgui_example_glfw_opengl3.py is an almost line by line translation of [a C++ example](https://github.com/ocornut/imgui/blob/master/examples/example_glfw_opengl3/main.cpp) from Dear ImGui.
            """,
        ),
    ]

    this_dir = os.path.dirname(__file__)
    demo_python_folder = this_dir + "/demos_immapp"
    demo_cpp_folder = os.path.abspath(demo_python_folder + "/../../demos_cpp/demos_immapp")
    demo_app_table = DemoAppTable(demo_apps, demo_python_folder, demo_cpp_folder)

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
