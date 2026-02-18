#include "library_config.h"
#include "imgui.h"
#include "im_anim.h"
#include "implot/implot.h"
#include "implot3d/implot3d.h"
#include <algorithm>
#include <cctype>
#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif

// Forward declarations for ImAnim demo windows
void ImAnimDemoBasicsWindow(bool create_window);
void ImAnimDemoWindow(bool create_window);
void ImAnimDocWindow(bool create_window);
void ImAnimUsecaseWindow(bool create_window);

namespace {

std::vector<LibraryConfig> CreateLibraryConfigs()
{
    std::vector<LibraryConfig> configs;


    // ImGui
    {
        LibraryConfig cfg;
        cfg.name = "ImGui";
        cfg.files = {
            {"imgui_demo", true, false,
             "https://github.com/pthom/imgui/blob/imgui_bundle/imgui_demo.cpp",
             "https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_imgui_manual/imgui_demo.py"},
            {"imgui", true, true,
             "https://github.com/pthom/imgui/blob/imgui_bundle/imgui.h",
             "https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui/__init__.pyi"},
            {"imgui_internal", true, true,
             "https://github.com/pthom/imgui/blob/imgui_bundle/imgui_internal.h",
             "https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui/internal.pyi"},
        };
        cfg.frameSetup = nullptr;
        cfg.showDemoWindow = [] {
            static bool do_create_window = false;
            ImGui::Checkbox("ImGui Demo in external window", &do_create_window);
            ImGui::SetItemTooltip("Useful to test \"Window Options\" below...");

            ImGui::Separator();
            ImGui::ShowDemoWindow_MaybeDocked(do_create_window);
        };
        configs.push_back(std::move(cfg));
    }

    // ImPlot
    {
        LibraryConfig cfg;
        cfg.name = "ImPlot";
        cfg.files = {
            {"implot_demo", true, false,
             "https://github.com/pthom/implot/blob/imgui_bundle/implot_demo.cpp",
             "https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_imgui_manual/implot_demo.py"},
            {"implot", true, true,
             "https://github.com/pthom/implot/blob/imgui_bundle/implot.h",
             "https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/implot/__init__.pyi"},
            {"implot_internal", true, true,
             "https://github.com/pthom/implot/blob/imgui_bundle/implot_internal.h",
             "https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/implot/internal.pyi"},
        };
        cfg.frameSetup = nullptr;
        cfg.showDemoWindow = [] {
            ImPlot::ShowDemoWindow_MaybeDocked(false);
        };
        configs.push_back(std::move(cfg));
    }

    // ImPlot3D
    {
        LibraryConfig cfg;
        cfg.name = "ImPlot3D";
        cfg.files = {
            {"implot3d_demo", true, false,
             "https://github.com/pthom/implot3d/blob/imgui_bundle/implot3d_demo.cpp",
             "https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_imgui_manual/implot3d_demo.py"},
            {"implot3d", true, true,
             "https://github.com/pthom/implot3d/blob/imgui_bundle/implot3d.h",
             "https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/implot3d/__init__.pyi"},
            {"implot3d_internal", true, true,
             "https://github.com/pthom/implot3d/blob/imgui_bundle/implot3d_internal.h",
             "https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/implot3d/internal.pyi"},
        };
        cfg.frameSetup = nullptr;
        cfg.showDemoWindow = [] {
            ImPlot3D::ShowDemoWindow_MaybeDocked(false);
        };
        configs.push_back(std::move(cfg));
    }

    // ImAnim
    {
        LibraryConfig cfg;
        cfg.name = "ImAnim";
        cfg.files = {
                {"im_anim_demo_basics", true, false,
                 "https://github.com/pthom/ImAnim/blob/imgui_bundle/im_anim_demo_basics.cpp",
                 "https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_imgui_manual/im_anim_demo_basics.py"},
                {"im_anim_demo", false, false,
                 "https://github.com/pthom/ImAnim/blob/imgui_bundle/im_anim_demo.cpp"},
                {"im_anim_doc", false, false,
                 "https://github.com/pthom/ImAnim/blob/imgui_bundle/im_anim_doc.cpp"},
                {"im_anim_usecase", false, false,
                 "https://github.com/pthom/ImAnim/blob/imgui_bundle/im_anim_usecase.cpp"},
                {"im_anim", true, true,
                 "https://github.com/pthom/ImAnim/blob/imgui_bundle/im_anim.h",
                 "https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/im_anim.pyi"},
            };
        cfg.frameSetup = [] {
            iam_update_begin_frame();
            iam_clip_update(ImGui::GetIO().DeltaTime);
        };
        cfg.showDemoWindow = [] {
            // For now, show all ImAnim windows (we'll refine this later)
            ImAnimDemoBasicsWindow(false);
        };
        configs.push_back(std::move(cfg));
    }

    return configs;
}

} // anonymous namespace

const std::vector<LibraryConfig>& GetAllLibraryConfigs()
{
    static std::vector<LibraryConfig> configs = CreateLibraryConfigs();
    return configs;
}

std::vector<DemoFileInfo> GetAllDemoFiles()
{
    std::vector<DemoFileInfo> allFiles;
    for (const auto& lib : GetAllLibraryConfigs())
    {
        for (const auto& file : lib.files)
        {
            allFiles.push_back(file);
        }
    }
    return allFiles;
}

// Current library selection (0 = first library)
static int g_currentLibraryIndex = 0;

int GetCurrentLibraryIndex()
{
    return g_currentLibraryIndex;
}

void SetCurrentLibraryIndex(int index)
{
    const auto& configs = GetAllLibraryConfigs();
    if (index >= 0 && index < (int)configs.size())
        g_currentLibraryIndex = index;
}

const LibraryConfig& GetCurrentLibrary()
{
    return GetAllLibraryConfigs()[g_currentLibraryIndex];
}

std::vector<DemoFileInfo> GetCurrentLibraryFiles()
{
    return GetCurrentLibrary().files;
}

// Single-library mode
static bool g_singleLibraryMode = false;

bool IsSingleLibraryMode()
{
    return g_singleLibraryMode;
}

void SetSingleLibraryMode(bool enabled)
{
    g_singleLibraryMode = enabled;
}

namespace {
    std::string ToLower(const std::string& s)
    {
        std::string result = s;
        std::transform(result.begin(), result.end(), result.begin(),
                       [](unsigned char c) { return std::tolower(c); });
        return result;
    }

    int FindLibraryIndexByName(const std::string& name)
    {
        std::string nameLower = ToLower(name);
        const auto& configs = GetAllLibraryConfigs();
        for (int i = 0; i < (int)configs.size(); ++i)
        {
            if (ToLower(configs[i].name) == nameLower)
                return i;
        }
        return -1;
    }
} // anonymous namespace

void ParseLibraryArg(int argc, char** argv)
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
        if (std::string(argv[i]) == "--lib")
        {
            libName = argv[i + 1];
            break;
        }
    }
#endif

    if (!libName.empty())
    {
        int idx = FindLibraryIndexByName(libName);
        if (idx >= 0)
        {
            SetCurrentLibraryIndex(idx);
            SetSingleLibraryMode(true);
        }
    }
}
