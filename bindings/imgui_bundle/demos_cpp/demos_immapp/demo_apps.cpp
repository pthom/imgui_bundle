#include "immapp/immapp.h"
#include "../demo_utils/demo_app_table.h"
#include <filesystem>


const std::string DOC = R"(
# HelloImGui and ImmApp

* [HelloImGui](https://github.com/pthom/hello_imgui) is a library based on ImGui that enables to easily create applications with ImGui.
  Link to the [API documentation](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md). Docking layout [documentation](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md#docking)
* [ImApp](https://github.com/pthom/imgui_bundle/blob/dev/bindings/imgui_bundle/immapp/immapp_cpp.pyi) (aka "Immediate App", a submodule of ImGuiBundle) is a thin extension of HelloImGui that enables to easily initialize the ImGuiBundle addons that require additional setup at startup.

## Demo applications
)";


// This returns a closure function that will later be invoked to run the app
std::function<void()> makeClosureDemoApps()
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
            How to run a *bare ImGui application*<br>
            imgui_example_glfw_opengl3.py is a direct adaptation of [a C++ example](https://github.com/ocornut/imgui/blob/master/examples/example_glfw_opengl3/main.cpp) from Dear ImGui.<br>
            You can configure and run imgui, opengl and glfw)"}
    };

    std::string thisDir = std::filesystem::path(__FILE__).parent_path().string();
    std::string demoCppFolder = thisDir;
    std::string demoPythonFolder = demoCppFolder + "/../../demos_python/demos_immapp";
    DemoAppTable demoAppTable(demoApps, demoPythonFolder, demoCppFolder);

    auto gui = [demoAppTable]() mutable
    {
        ImGuiMd::RenderUnindented(DOC);
        demoAppTable.Gui();
    };
    return gui;
}


int main()
{
    auto gui = makeClosureDemoApps();

    ImmApp::RunWithMarkdown(gui, "Immediate Apps", false, false, {1000, 800});
}
