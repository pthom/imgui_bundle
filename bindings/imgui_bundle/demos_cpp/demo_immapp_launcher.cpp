// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "immapp/immapp.h"
#include "demo_utils/demo_app_table.h"
#include "demo_utils/api_demos.h"
#include <filesystem>


const std::string DOC = R"(
# HelloImGui and ImmApp

* [HelloImGui](https://github.com/pthom/hello_imgui) is a library based on ImGui that enables to easily create applications with ImGui.
  Link to the [API documentation](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md). Docking layout [documentation](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md#docking)
* [ImApp](https://github.com/pthom/imgui_bundle/blob/dev/bindings/imgui_bundle/immapp/immapp_cpp.pyi) (aka "Immediate App", a submodule of ImGuiBundle) is a thin extension of HelloImGui that enables to easily initialize the ImGuiBundle addons that require additional setup at startup.

## Demo applications
)";


// This returns a closure function that will later be invoked to run the app
std::function<void()> makeGui()
{
    std::vector<DemoApp> demoApps = {
        DemoApp{"demo_hello_world", "Hello world demo: how to create an app with ImmApp in a few lines."},
        DemoApp{"demo_parametric_curve","Illustration of the Immediate GUI paradigm, with a simple parametric curve"},
        DemoApp{"demo_assets", "How to load assets with HelloImGui"},
        DemoApp{
            "demo_docking",
            """How to build complex applications layouts, with dockable panels,that can even become independent windows. How to customize the theme.""",
        },
        DemoApp{"demo_implot_markdown", "How to quickly run an app that uses implot and/or markdown with ImmApp"},
        DemoApp{
            "demo_powersave", "How to have smooth animations, and how spare the CPU when idling"
        },
        DemoApp{"demo_custom_font", "How to load custom fonts"},
        DemoApp{"demo_command_palette", "a Sublime Text or VSCode style command palette in ImGui"},
        DemoApp{"haiku_implot_heart", "Share some love for ImGui and ImPlot"},
        DemoApp{
            "imgui_example_glfw_opengl3",
            "Python translation of the [GLFW+OpenGL3 example](https://github.com/ocornut/imgui/blob/master/examples/example_glfw_opengl3/main.cpp) from Dear ImGui. Demonstrates how to port from C++ to Python."
        },
        DemoApp{"imgui_example_glfw_opengl2","Python translation of the [GLFW+OpenGL2 example](https://github.com/ocornut/imgui/blob/master/examples/example_glfw_opengl2/main.cpp) from Dear ImGui"},
        DemoApp{
            "imgui_example_sdl2_opengl3",
            "Python translation of the [SDL2+OpenGL3 example](https://github.com/ocornut/imgui/blob/master/examples/example_sdl2_opengl3/main.cpp) from Dear ImGui",
        },
        DemoApp{"demo_drag_and_drop", "Drag and drop demo"},
    };

    DemoAppTable demoAppTable(demoApps, DemoPythonFolder() + "/demos_immapp/", DemoCppFolder() + "/demos_immapp/");
    auto gui = [demoAppTable]() mutable
    {
        ImGuiMd::RenderUnindented(DOC);
        demoAppTable.Gui();
    };
    return gui;
}


void demo_immapp_launcher()
{
    static std::function<void()> gui = makeGui();
    gui();
}
