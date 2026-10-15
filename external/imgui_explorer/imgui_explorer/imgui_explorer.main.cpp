#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/hello_imgui_font.h"
#include "immapp/runner.h"
#include "imgui_explorer.h"
#include "src/demo_code_viewer.h"
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
    // if (libName.empty())
    //     libName = "imgui"; // Temporarily use imgui only on the base url
    // if (libName == "all")
    //     libName = ""; // Temporarily use imgui only on the base url
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

// The section to open: ?demo=<section> in the URL, --demo <section> on the command line (a path such as
// "Plots/Line Plots", or words of it)
std::string ParseDemoArg(int argc, char** argv)
{
#ifdef __EMSCRIPTEN__
    (void)argc; (void)argv;
    const char* result = emscripten_run_script_string("new URLSearchParams(window.location.search).get('demo') || ''");
    return result ? result : "";
#else
    for (int i = 1; i < argc - 1; ++i)
        if (std::string(argv[i]) == "--demo")
            return argv[i + 1];
    return "";
#endif
}

// Whether the page takes the pictures of the API pages (ci_scripts/api_pictures.py adds &shot=1 to its links)
bool IsPictureMode()
{
#ifdef __EMSCRIPTEN__
    return emscripten_run_script_int("new URLSearchParams(window.location.search).has('shot') ? 1 : 0") != 0;
#else
    return false;
#endif
}

// The code's language: ?lang=python (or cpp) in the URL, --lang python on the command line
std::string ParseLangArg(int argc, char** argv)
{
#ifdef __EMSCRIPTEN__
    (void)argc; (void)argv;
    const char* result = emscripten_run_script_string("new URLSearchParams(window.location.search).get('lang') || ''");
    return result ? result : "";
#else
    for (int i = 1; i < argc - 1; ++i)
        if (std::string(argv[i]) == "--lang")
            return argv[i + 1];
    return "";
#endif
}


int main(int argc, char** argv)
{
    auto libraryFromString = [](const std::string& s) -> std::optional<ImGuiExplorerLibrary> {
        auto lower = [](std::string t) { std::transform(t.begin(), t.end(), t.begin(), ::tolower); return t; };
        std::string sl = lower(s);
        if (sl == "imgui")   return ImGuiExplorerLibrary::ImGui;
        if (sl == "implot")  return ImGuiExplorerLibrary::ImPlot;
        if (sl == "implot3d")return ImGuiExplorerLibrary::ImPlot3D;
        if (sl == "imanim")  return ImGuiExplorerLibrary::ImAnim;
        return std::nullopt;
    };
    std::optional<ImGuiExplorerLibrary> library = libraryFromString(ParseLibraryArg(argc, argv));
    DemoCodeViewer_EnableLinks(ParseDemoArg(argc, argv));
    if (ParseLangArg(argc, argv) == "python")
        DemoCodeViewer_SetShowPython(true);

    HelloImGui::RunnerParams runnerParams;

    runnerParams.appWindowParams.windowTitle = "Dear ImGui Explorer: An Interactive Manual for Dear ImGui, ImPlot & ImPlot3D";
    runnerParams.appWindowParams.windowGeometry.size = {1400, 900};
    runnerParams.imGuiWindowParams.configWindowsMoveFromTitleBarOnly = false;
    runnerParams.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::ProvideFullScreenWindow;
    runnerParams.imGuiWindowParams.enableViewports = false;

    runnerParams.callbacks.ShowGui = [library]() { ShowImGuiExplorerGui_Cpp(library, true); };

    runnerParams.fpsIdling.fpsIdle = 30.f; // The demos animate, and are not ours to mark as live (SetItemIsLive)

    runnerParams.iniClearPreviousSettings = true; // start with a clean layout each time (for demo purposes)

    // Use proggy forever with the code below (disabled for the moment, waiting for Omar confirmation)
    // runnerParams.callbacks.LoadAdditionalFonts = []() {
    //     ImGui::GetIO().Fonts->AddFontDefaultVector();
    //     HelloImGui::FontLoadingParams faParams;
    //     faParams.mergeToLastFont = true;
    //     HelloImGui::LoadFont("fonts/fontawesome-webfont.ttf", 13.f, faParams);
    //     ImGui::GetStyle().FontSizeBase = 16.f;
    // };

    runnerParams.callbacks.SetupImGuiConfig = [] {
        ImGui::GetIO().ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
    };
    if (IsPictureMode())  // opaque windows: the demo's windows (Examples, Tools) show nothing of the windows below
        runnerParams.callbacks.PreNewFrame = [] {  // (at each frame: hello_imgui applies its theme after PostInit)
            ImGui::GetStyle().Colors[ImGuiCol_WindowBg].w = 1.f;
        };

    ImmApp::AddOnsParams addons;
    addons.withMarkdown = true;
    addons.withImplot = true;
    addons.withImplot3d = true;
    addons.withImAnim = true;

    // start with a clean layout each time (for demo purposes)
    runnerParams.iniClearPreviousSettings = true;

    ImmApp::Run(runnerParams, addons);
    return 0;
}
