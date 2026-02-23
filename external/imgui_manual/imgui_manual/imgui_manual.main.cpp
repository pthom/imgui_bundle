#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/hello_imgui_font.h"
#include "immapp/runner.h"
#include "imgui_manual.h"
#include "imgui.h"
#include <algorithm>
#include <cctype>
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
        auto lower = [](std::string t) { std::transform(t.begin(), t.end(), t.begin(), ::tolower); return t; };
        std::string sl = lower(s);
        if (sl == "imgui")   return ImGuiManualLibrary::ImGui;
        if (sl == "implot")  return ImGuiManualLibrary::ImPlot;
        if (sl == "implot3d")return ImGuiManualLibrary::ImPlot3D;
        if (sl == "imanim")  return ImGuiManualLibrary::ImAnim;
        return std::nullopt;
    };
    std::optional<ImGuiManualLibrary> library = libraryFromString(ParseLibraryArg(argc, argv));

    HelloImGui::RunnerParams runnerParams;

    runnerParams.appWindowParams.windowTitle = "Dear ImGui Manual";
    runnerParams.appWindowParams.windowGeometry.size = {1400, 900};
    runnerParams.imGuiWindowParams.configWindowsMoveFromTitleBarOnly = false;
    runnerParams.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::ProvideFullScreenWindow;
    runnerParams.imGuiWindowParams.enableViewports = false;

    runnerParams.callbacks.ShowGui = [library]() { ShowImGuiManualGui(library, ImGuiManualCppOrPython::Cpp, true); };

    runnerParams.fpsIdling.fpsIdle = 24.f; // When idling, keep a reasonable framerate

    runnerParams.iniClearPreviousSettings = true; // start with a clean layout each time (for demo purposes)
    runnerParams.callbacks.LoadAdditionalFonts = []() {
        ImGui::GetIO().Fonts->AddFontDefaultVector();
        HelloImGui::FontLoadingParams faParams;
        faParams.mergeToLastFont = true;
        HelloImGui::LoadFont("fonts/fontawesome-webfont.ttf", 13.f, faParams);
    };

    ImmApp::AddOnsParams addons;
    addons.withMarkdown = true;
    addons.withImplot = true;
    addons.withImplot3d = true;
    addons.withImAnim = true;
    ImmApp::Run(runnerParams, addons);
    return 0;
}
