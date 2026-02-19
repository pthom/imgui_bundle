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
    std::string libName = ParseLibraryArg(argc, argv);
    if (!libName.empty())
        ImGuiManual::SetLibrary(libName);

    HelloImGui::RunnerParams runnerParams;

    runnerParams.appWindowParams.windowTitle = "Dear ImGui Manual";
    runnerParams.appWindowParams.windowGeometry.size = {1400, 900};

    runnerParams.callbacks.ShowGui = []() { ImGuiManual::ShowGui(true); };

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
