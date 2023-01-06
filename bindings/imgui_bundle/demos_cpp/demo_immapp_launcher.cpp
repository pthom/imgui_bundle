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
        DemoApp{"demo_hello_world", "Hello world demo: how to start an app with ImmApp in as few lines as possible"},
        DemoApp{"demo_assets", "How to load assets with HelloImGui"},
        DemoApp{
            "demo_docking",
            """How to build complex applications layouts, with dockable panels,that can even become independent windows. How to customize the theme.""",
        },
        DemoApp{"demo_implot_markdown", "How to quickly run an app that uses implot and/or markdown with ImmApp"},
        DemoApp{
            "demo_powersave", "How to have smooth animations, and how to let the application save CPU when idle"
        },
        DemoApp{"demo_custom_font", "How to load custom fonts"},
        DemoApp{"demo_command_palette", "a Sublime Text or VSCode style command palette in ImGui"},
        DemoApp{"haiku_implot_heart", "Share some love for ImGui and ImPlot"},
        DemoApp{
            "imgui_example_glfw_opengl3",
            R"(
            How to port an existing ImGui application to python<br>
            imgui_example_glfw_opengl3.py is an almost line by line translation of [a C++ example](https://github.com/ocornut/imgui/blob/master/examples/example_glfw_opengl3/main.cpp) from Dear ImGui.
            )"}
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
