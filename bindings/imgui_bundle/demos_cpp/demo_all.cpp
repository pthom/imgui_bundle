#include "immapp/immapp.h"
#include "hello_imgui/hello_imgui.h"
#include "immapp/snippets.h"
#include "demo_utils/api_demos.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"

#include <functional>
#include <fplus/fplus.hpp>

void demo_immapp_launcher();
void demo_text_edit();
void demo_imgui_bundle();
void demo_imgui_show_demo_window();
void demo_widgets();
void demo_implot();
void demo_imgui_md();
void demo_immvision_launcher();
void demo_imguizmo_launcher();
void demo_tex_inspect_launcher();
void demo_node_editor_launcher();
void demo_immapp_notebook();
void demo_themes();
void demo_logger();
void demo_utils();


using VoidFunction = std::function<void(void)>;


void ShowModuleDemo(const std::string& demoModule, VoidFunction demoFunction)
{
    static TextEditorBundle::SnippetData snippet;
    static bool wasInitialized;
    static std::string lastModule;

    if (!wasInitialized)
    {
        snippet.Language = TextEditorBundle::SnippetLanguage::Cpp;
        wasInitialized = true;
    }

    if (demoModule != lastModule)
    {
        std::string code = ReadCppCode(demoModule);
        snippet.Code = code;
    }

    if (ImGui::CollapsingHeader("Code for this demo"))
        TextEditorBundle::ShowCodeSnippet(snippet);

    demoFunction();
}


int main()
{
    HelloImGui::SetAssetsFolder(DemosAssetsFolder());
    //###############################################################################################
    // Part 1: Define the runner params
    //###############################################################################################

    // Hello ImGui params (they hold the settings as well as the Gui callbacks)
    HelloImGui::RunnerParams runnerParams;
    // Window size and title
    runnerParams.appWindowParams.windowTitle = "ImGui Bundle";
    runnerParams.appWindowParams.windowGeometry.size = {1400, 900};

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

    auto addDockableWindow = [&dockableWindows](
        const std::string label,
        const std::string demoModule,
        VoidFunction demoFunction,
        const std::string& dockSpaceName = "MainDockSpace")
    {
        HelloImGui::DockableWindow window;
        window.label = label;
        window.dockSpaceName = dockSpaceName;

        window.GuiFunction = [demoModule, demoFunction]()
        {
            ShowModuleDemo(demoModule, demoFunction);
        };
        dockableWindows.push_back(window);
    };

#define ADD_DOCKABLE_WINDOW(tab_title, demo_name) \
    addDockableWindow(tab_title, #demo_name, demo_name)

    ADD_DOCKABLE_WINDOW("ImGui Bundle", demo_imgui_bundle);
    ADD_DOCKABLE_WINDOW("Dear ImGui Demo", demo_imgui_show_demo_window);
    ADD_DOCKABLE_WINDOW("Immediate Apps", demo_immapp_launcher);
    ADD_DOCKABLE_WINDOW("Implot", demo_implot);
    ADD_DOCKABLE_WINDOW("Node Editor", demo_node_editor_launcher);
    ADD_DOCKABLE_WINDOW("Markdown", demo_imgui_md);
    ADD_DOCKABLE_WINDOW("Text Editor", demo_text_edit);
    ADD_DOCKABLE_WINDOW("Widgets", demo_widgets);
    ADD_DOCKABLE_WINDOW("ImmVision", demo_immvision_launcher);
    ADD_DOCKABLE_WINDOW("imgui_tex_inspect", demo_tex_inspect_launcher);
    ADD_DOCKABLE_WINDOW("ImGuizmo", demo_imguizmo_launcher);
    ADD_DOCKABLE_WINDOW("Themes", demo_themes);
    ADD_DOCKABLE_WINDOW("Logger", demo_logger);
    ADD_DOCKABLE_WINDOW("Notebook", demo_immapp_notebook);

    runnerParams.dockingParams.dockableWindows = dockableWindows;

    // the main gui is only responsible to give focus to ImGui Bundle dockable window
    auto showGui = [&runnerParams]
    {
        static int nbFrames = 0;
        if (nbFrames == 1)
        {
            // Focus cannot be given at frame 0, since some additional windows will
            // be created after (and will steal the focus)
            runnerParams.dockingParams.focusDockableWindow("ImGui Bundle");
        }
        nbFrames += 1;
    };

    runnerParams.callbacks.ShowGui = showGui;

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
}
