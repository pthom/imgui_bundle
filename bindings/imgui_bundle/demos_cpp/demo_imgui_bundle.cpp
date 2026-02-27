// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "immapp/immapp.h"
#include "hello_imgui/hello_imgui.h"
#include "immapp/snippets.h"
#include "demo_utils/api_demos.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"

#include <functional>
#include <map>

void demo_immapp_launcher();
void demo_nanovg_launcher();
void demo_text_edit();
void demo_imgui_bundle_intro();
void demo_imgui_show_demo_window();
void demo_widgets();
void demo_implot();
void demo_imgui_md();
void demo_immvision_launcher();
void demo_imguizmo_launcher();
void demo_tex_inspect_launcher();
void demo_node_editor_launcher();
void demo_themes();
void demo_logger();
void demo_utils();
void demo_im_anim();



using VoidFunction = std::function<void(void)>;

static std::map<std::string, bool> gShowCodeStates;

void ShowModuleDemo(const std::string& demoFilename, VoidFunction demoFunction, bool showCode)
{
    if (ImGui::GetFrameCount() < 2) // cf https://github.com/pthom/imgui_bundle/issues/293
        return;
    if (showCode)
    {
        bool current = gShowCodeStates[demoFilename];
        if (ImGui::Checkbox(("Show code##" + demoFilename).c_str(), &current))
            gShowCodeStates[demoFilename] = current;
        if (current)
            ShowPythonVsCppFile(demoFilename.c_str(), 40);
    }
    demoFunction();
}


struct DemoDetails
{
    std::string Label;
    std::string DemoFilename;
    VoidFunction DemoFunction;
    bool ShowCode = false;
};

struct DemoGroup
{
    std::string Label;
    std::vector<DemoDetails> Demos;
};

void ShowGroupGui(const DemoGroup& group)
{
    if (ImGui::GetFrameCount() < 2)
        return;
    for (const auto& demo : group.Demos)
    {
        if (ImGui::CollapsingHeader(demo.Label.c_str()))
        {
            ImGui::Indent();
            ShowModuleDemo(demo.DemoFilename, demo.DemoFunction, demo.ShowCode);
            ImGui::Unindent();
        }
    }
}


int main(int, char **)
{
    ChdirBesideAssetsFolder();
    //###############################################################################################
    // Part 1: Define the runner params
    //###############################################################################################

    // Hello ImGui params (they hold the settings as well as the Gui callbacks)
    HelloImGui::RunnerParams runnerParams;
    // Window size and title
    runnerParams.appWindowParams.windowTitle = "Dear ImGui Bundle Explorer";
    runnerParams.appWindowParams.windowGeometry.size = {1400, 950};

    // Menu bar
    runnerParams.imGuiWindowParams.showMenuBar = true;
    runnerParams.imGuiWindowParams.showStatusBar = true;

    //###############################################################################################
    // Part 2: Define the application layout and windows
    //###############################################################################################

    // First, tell HelloImGui that we want full screen dock space (this will create "MainDockSpace")
    runnerParams.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::ProvideFullScreenDockSpace;
    // In this demo, we also demonstrate multiple viewports.
    // you can drag windows outside out the main window in order to put their content into new native windows
    runnerParams.imGuiWindowParams.enableViewports = true;

    //
    // Define our dockable windows : each window provide a Gui callback, and will be displayed
    // in a docking split.
    //
    std::vector<HelloImGui::DockableWindow> dockableWindows;

#define DEMO_DETAILS(label, function_name)           DemoDetails{ label, #function_name, function_name, false }
#define DEMO_DETAILS_WITH_CODE(label, function_name) DemoDetails{ label, #function_name, function_name, true  }

    // --- Standalone tabs (no grouping) ---
    std::vector<DemoDetails> standaloneDemos {
        DEMO_DETAILS("Intro",       demo_imgui_bundle_intro),
        DEMO_DETAILS("Dear ImGui",  demo_imgui_show_demo_window),
        DEMO_DETAILS("Demo Apps",   demo_immapp_launcher),
    };

    for (const auto& demo : standaloneDemos)
    {
        HelloImGui::DockableWindow window;
        window.label = demo.Label;
        window.dockSpaceName = "MainDockSpace";
        window.GuiFunction = [demo]()
        {
            ShowModuleDemo(demo.DemoFilename, demo.DemoFunction, demo.ShowCode);
        };
        dockableWindows.push_back(window);
    }

    // --- Grouped tabs (sub-demos shown as collapsing headers) ---
    std::vector<DemoGroup> groups {
        { "Visualization", {
            DEMO_DETAILS(          "Plots with ImPlot and ImPlot3D",  demo_implot),
            DEMO_DETAILS(          "ImmVision - Image analyzer",      demo_immvision_launcher),
            DEMO_DETAILS(          "ImGuizmo - Immediate Mode 3D Gizmo", demo_imguizmo_launcher),
#ifdef IMGUI_BUNDLE_WITH_NANOVG
            DEMO_DETAILS(          "NanoVG - 2D Vector Drawing",      demo_nanovg_launcher),
#endif
        }},
        { "Widgets", {
            DEMO_DETAILS_WITH_CODE("Markdown - Rich Text Rendering",     demo_imgui_md),
            DEMO_DETAILS_WITH_CODE("Text Editor - Code Editing Widget",  demo_text_edit),
            DEMO_DETAILS_WITH_CODE("Misc Widgets - Knobs, Toggles, ...", demo_widgets),
            DEMO_DETAILS_WITH_CODE("Logger - Log Window Widget",         demo_logger),
            DEMO_DETAILS(          "Tex Inspect - Texture Inspector",    demo_tex_inspect_launcher),
        }},
        { "Tools", {
            DEMO_DETAILS(          "Node Editor - Visual Node Graphs",       demo_node_editor_launcher),
            DEMO_DETAILS_WITH_CODE("Themes - Style & Color Customization",   demo_themes),
            DEMO_DETAILS(          "ImAnim - Animation Library",             demo_im_anim),
        }},
    };

    for (const auto& group : groups)
    {
        HelloImGui::DockableWindow window;
        window.label = group.Label;
        window.dockSpaceName = "MainDockSpace";
        window.GuiFunction = [group]()
        {
            ShowGroupGui(group);
        };
        dockableWindows.push_back(window);
    }

    runnerParams.dockingParams.dockableWindows = dockableWindows;

    // the main gui is only responsible to give focus to ImGui Bundle dockable window
    auto showGui = [&runnerParams]
    {
        static int nbFrames = 0;
        if (nbFrames == 1)
        {
            // Focus cannot be given at frame 0, since some additional windows will
            // be created after (and will steal the focus)
            runnerParams.dockingParams.focusDockableWindow("Dear ImGui Bundle");
        }
        nbFrames += 1;
    };

    auto showEditFontScaleInStatusBar = []()
    {
        ImGui::SetNextItemWidth(ImGui::GetContentRegionAvail().x / 10.f);
        ImGui::SliderFloat("Font scale", & ImGui::GetStyle().FontScaleMain, 0.5f, 5.f);
    };
    runnerParams.callbacks.ShowStatus = showEditFontScaleInStatusBar;

    runnerParams.callbacks.ShowGui = showGui;
    runnerParams.useImGuiTestEngine = true;

    runnerParams.callbacks.SetupImGuiConfig = [] {
        ImGui::GetIO().ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
    };

    // ################################################################################################
    // Part 3: Run the app
    // ################################################################################################
    auto addons = ImmApp::AddOnsParams();
    addons.withMarkdown = true;
    addons.withNodeEditor = true;
    addons.withImplot = true;
    addons.withImplot3d = true;
    addons.withTexInspect = true;
    addons.withImAnim = true;

    runnerParams.iniClearPreviousSettings = true;

    ImmApp::Run(runnerParams, addons);

    return 0;
}
