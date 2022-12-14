import os

from imgui_bundle import imgui_md
from imgui_bundle import immapp
from imgui_bundle.demos.demo_utils.api_demos import GuiFunction
from imgui_bundle.demos.demo_utils.demo_app_table import DemoAppTable, DemoApp


DOC = """
# HelloImGui and ImmApp

* [HelloImGui](https://github.com/pthom/hello_imgui) is a library based on ImGui that enables to easily create applications with ImGui.
  Link to the [API documentation](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md). Docking layout [documentation](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md#docking)
* [ImApp](https://github.com/pthom/imgui_bundle/blob/dev/bindings/imgui_bundle/immapp/immapp_cpp.pyi) (aka "Immediate App", a submodule of ImGuiBundle) is a thin extension of HelloImGui that enables to easily initialize the ImGuiBundle addons that require additional setup at startup. 

## Demo applications
    """


# This returns a closure function that will later be invoked to run the app
def make_closure_demo_apps() -> GuiFunction:
    demo_apps = [
        DemoApp("imgui_example_glfw_opengl3.py", """
                    How to run a *bare ImGui application*<br>
                    imgui_example_glfw_opengl3.py is a direct adaptation of [a C++ example](https://github.com/ocornut/imgui/blob/master/examples/example_glfw_opengl3/main.cpp) from Dear ImGui.<br>
                    You can configure and run imgui, opengl and glfw (or sdl, etc.) manually as show in this example"""),
        DemoApp("demo_hello_world.py",
                "Hello world demo: how to start an app with ImmApp in as few lines as possible"),
        DemoApp("demo_assets.py", "How to load assets with HelloImGui"),
        DemoApp("demo_docking.py","""How to build complex applications layouts, with dockable panels,that can even become independent windows. How to customize the theme."""
                ),
        DemoApp("demo_implot_markdown.py", "How to quickly run an app that uses implot and/or markdown with ImmApp"),
        DemoApp("demo_powersave.py", "How to have smooth animations, and how to let the application save CPU when idle"),
        DemoApp("demo_custom_font.py", "How to load custom fonts"),
        DemoApp("../haikus/haiku_implot_heart.py", "Animated heart"),
    ]

    idx_initial_app = 2
    this_dir = os.path.dirname(__file__)
    demo_app_table = DemoAppTable(demo_apps, this_dir, idx_initial_app)

    def gui():
        nonlocal demo_apps
        imgui_md.render(DOC)
        demo_app_table.gui()

    return gui


def main():
    gui = make_closure_demo_apps()
    immapp.run(gui, with_markdown=True, window_size=(1000, 800))  # type: ignore


if __name__ == "__main__":
    main()
