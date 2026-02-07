#include "library_config.h"
#include "imgui.h"
#include "im_anim.h"
#include "implot/implot.h"
#include "implot3d/implot3d.h"

// Forward declarations for ImAnim demo windows
void ImAnimDemoBasicsWindow(bool create_window);
void ImAnimDemoWindow(bool create_window);
void ImAnimDocWindow(bool create_window);
void ImAnimUsecaseWindow(bool create_window);

namespace {

std::vector<LibraryConfig> CreateLibraryConfigs()
{
    std::vector<LibraryConfig> configs;

    // ImAnim
    {
        LibraryConfig cfg;
        cfg.name = "ImAnim";
        cfg.files = {
            {"im_anim_demo_basics", true},   // has Python
            {"im_anim_demo", false},
            {"im_anim_doc", false},
            {"im_anim_usecase", false},
        };
        cfg.frameSetup = [] {
            iam_update_begin_frame();
            iam_clip_update(ImGui::GetIO().DeltaTime);
        };
        cfg.showDemoWindow = [](bool create_window) {
            // For now, show all ImAnim windows (we'll refine this later)
            ImAnimDemoBasicsWindow(create_window);
        };
        configs.push_back(std::move(cfg));
    }

    // ImGui
    {
        LibraryConfig cfg;
        cfg.name = "ImGui";
        cfg.files = {
            {"imgui_demo", true},  // has Python (not line-by-line match)
        };
        cfg.frameSetup = nullptr;
        cfg.showDemoWindow = [](bool create_window) {
            (void)create_window;
            ImGui::ShowDemoWindow();
        };
        configs.push_back(std::move(cfg));
    }

    // ImPlot
    {
        LibraryConfig cfg;
        cfg.name = "ImPlot";
        cfg.files = {
            {"implot_demo", true},
        };
        cfg.frameSetup = nullptr;
        cfg.showDemoWindow = [](bool create_window) {
            (void)create_window;
            ImPlot::ShowDemoWindow();
        };
        configs.push_back(std::move(cfg));
    }

    // ImPlot3D
    {
        LibraryConfig cfg;
        cfg.name = "ImPlot3D";
        cfg.files = {
            {"implot3d_demo", true},
        };
        cfg.frameSetup = nullptr;
        cfg.showDemoWindow = [](bool create_window) {
            (void)create_window;
            ImPlot3D::ShowDemoWindow();
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
