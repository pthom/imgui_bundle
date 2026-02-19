#include "hello_imgui/hello_imgui.h"
#include "immapp/runner.h"
#include "imgui_manual.h"
#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif

std::string ParseLibraryArg(int argc, char** argv)
{
    std::string libName;

#ifdef __EMSCRIPTEN__
    // Read ?lib=<name> from URL query parameters
    (void)argc; (void)argv;
    const char* result = emscripten_run_script_string(
        "new URLSearchParams(window.location.search).get('lib') || ''"
    );
    if (result && result[0] != '\0')
        libName = result;
#else
    // Read --lib <name> from command-line arguments
    for (int i = 1; i < argc - 1; ++i)
    {
        if (std::string(argv[i]) == "--lib" || std::string(argv[i]) == "-lib")
        {
            libName = argv[i + 1];
            break;
        }
    }
#endif

    return libName;
}


int main(int argc, char** argv)
{
    auto libraryFromString = [](const std::string& s) -> std::optional<ImGuiManualLibrary> {
        if (s == "ImGui")    return ImGuiManualLibrary::ImGui;
        if (s == "ImPlot")   return ImGuiManualLibrary::ImPlot;
        if (s == "ImPlot3D") return ImGuiManualLibrary::ImPlot3D;
        if (s == "ImAnim")   return ImGuiManualLibrary::ImAnim;
        return std::nullopt;
    };
    std::optional<ImGuiManualLibrary> library = libraryFromString(ParseLibraryArg(argc, argv));

    HelloImGui::RunnerParams runnerParams;

    runnerParams.appWindowParams.windowTitle = "Dear ImGui Manual";
    runnerParams.appWindowParams.windowGeometry.size = {1400, 900};

    runnerParams.callbacks.ShowGui = [library]() { ShowImGuiManualGui(library, ImGuiManualCppOrPython::Cpp, true); };

    runnerParams.fpsIdling.fpsIdle = 24.f; // When idling, keep a reasonable framerate

    runnerParams.iniClearPreviousSettings = true; // start with a clean layout each time (for demo purposes)

    ImmApp::AddOnsParams addons;
    addons.withMarkdown = true;
    addons.withImplot = true;
    addons.withImplot3d = true;
    addons.withImAnim = true;
    ImmApp::Run(runnerParams, addons);
    return 0;
}
