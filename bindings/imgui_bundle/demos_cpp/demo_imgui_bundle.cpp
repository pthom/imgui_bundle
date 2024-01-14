// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "immapp/immapp.h"
#include "hello_imgui/hello_imgui.h"
#include "immapp/snippets.h"
#include "demo_utils/api_demos.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"

#include <functional>

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


using VoidFunction = std::function<void(void)>;


void ShowModuleDemo(const std::string& demoFilename, VoidFunction demoFunction)
{

    if (ImGui::CollapsingHeader("Code for this demo"))
        ShowPythonVsCppFile(demoFilename.c_str());
    demoFunction();
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
    runnerParams.appWindowParams.windowTitle = "Dear ImGui Bundle interactive manual";
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

    struct DemoDetails
    {
        std::string Label;
        std::string DemoFilename;
        VoidFunction DemoFunction;
    };

    auto addDemoDockableWindow = [&dockableWindows](const DemoDetails& demoDetails)
    {
        HelloImGui::DockableWindow window;
        window.label = demoDetails.Label;
        window.dockSpaceName = "MainDockSpace";
        window.GuiFunction = [&demoDetails]()
        {
            ShowModuleDemo(demoDetails.DemoFilename, demoDetails.DemoFunction);
        };
        dockableWindows.push_back(window);
    };

#define DEMO_DETAILS(label, function_name) DemoDetails{ label, #function_name, function_name }

    std::vector<DemoDetails> demos {
        DEMO_DETAILS("Dear ImGui Bundle", demo_imgui_bundle_intro),
        DEMO_DETAILS("Dear ImGui", demo_imgui_show_demo_window),
        DEMO_DETAILS("Immediate Apps", demo_immapp_launcher),
        DEMO_DETAILS("Implot", demo_implot),
        DEMO_DETAILS("Node Editor", demo_node_editor_launcher),
        DEMO_DETAILS("Markdown", demo_imgui_md),
        DEMO_DETAILS("Text Editor", demo_text_edit),
        DEMO_DETAILS("Widgets", demo_widgets),
        DEMO_DETAILS("ImmVision", demo_immvision_launcher),
#ifdef IMGUI_BUNDLE_WITH_NANOVG
        DEMO_DETAILS("NanoVG", demo_nanovg_launcher),
#endif
        DEMO_DETAILS("ImGuizmo", demo_imguizmo_launcher),
        DEMO_DETAILS("Themes", demo_themes),
        DEMO_DETAILS("Logger", demo_logger),
        DEMO_DETAILS("tex_inspect", demo_tex_inspect_launcher),
    };

    for (const auto& demo: demos)
        addDemoDockableWindow(demo);

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

    runnerParams.callbacks.ShowGui = showGui;
    runnerParams.useImGuiTestEngine = true;

    // ################################################################################################
    // Part 3: Run the app
    // ################################################################################################
    auto addons = ImmApp::AddOnsParams();
    addons.withMarkdown = true;
    addons.withNodeEditor = true;
    addons.withMarkdown = true;
    addons.withImplot = true;
    addons.withTexInspect = true;
    ImmApp::Run(runnerParams, addons);

    return 0;
}
