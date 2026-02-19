#include "library_config.h"
#include "imgui.h"
#include "im_anim.h"
#include "implot/implot.h"
#include "implot3d/implot3d.h"
#include <algorithm>
#include <cctype>

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
        cfg.mdIntro = "Dear ImGui - Bloat-free Graphical User interface | [Repository](https://github.com/ocornut/imgui) | [FAQ](https://github.com/ocornut/imgui/blob/master/docs/FAQ.md) | [Wiki](https://github.com/ocornut/imgui/wiki) | [dearimgui.com](https://www.dearimgui.com/)";
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
        cfg.mdIntro = "ImPlot - Immediate Mode Plotting for Dear ImGui | [Repository](https://github.com/epezent/implot)";
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
        cfg.mdIntro = "ImPlot3D - Immediate Mode 3D Plotting for Dear ImGui | [Repository](https://github.com/brenocq/implot3d/)";
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
        cfg.mdIntro = "ImAnim - Animation Engine for Dear ImGui | [Repository](https://github.com/soufianekhiat/ImAnim) | [Docs](https://github.com/soufianekhiat/ImAnim/tree/main/docs)";
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


void SetSingleLibraryMode(std::string libname)
{
    int idx = FindLibraryIndexByName(libname);
    if (idx >= 0)
    {
        SetCurrentLibraryIndex(idx);
        g_singleLibraryMode = true;
    }
    else
    {
        IM_ASSERT(false && "SetSingleLibraryMode: Failed to find the current library name");
    }
}