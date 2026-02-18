#include "hello_imgui/hello_imgui.h"
#include "immapp/runner.h"
#include "im_anim.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "demo_code_viewer.h"
#include "imgui_demo_marker_hooks.h"
#include "library_config.h"

#include <string>
void OpenUrl(const std::string &url);

// Callback invoked when a demo marker is hovered (with tracking enabled)
void OnDemoMarkerHook(const char* file, int line, const char* section)
{
    static int last_line = -1;
    if (line == last_line)
        return;
    last_line = line;
    DemoCodeViewer_ShowCodeAt(file, line, section);
}

void OnPostInit()
{
    // Initialize the code viewer (loads source files from assets)
    DemoCodeViewer_Init();

    // Set up the demo marker hook
    GImGuiDemoMarkerHook = OnDemoMarkerHook;
}

// Top toolbar: library selection buttons + C++/Python toggle
void ShowLibraryToolbar()
{
    ImGui::BeginHorizontal("LibraryToolbar", ImVec2(ImGui::GetContentRegionAvail().x, 0.f));

    ImGui::Spring(1.f);

    const auto& libs = GetAllLibraryConfigs();
    int currentIdx = GetCurrentLibraryIndex();

    for (size_t i = 0; i < libs.size(); ++i)
    {
        ImGui::PushStyleVar(ImGuiStyleVar_FrameRounding, 10.f);
        bool isSelected = ((int)i == currentIdx);
        if (isSelected)
            ImGui::PushStyleColor(ImGuiCol_Button, ImGui::GetStyleColorVec4(ImGuiCol_ButtonActive));
        if (ImGui::Button(libs[i].name.c_str(), HelloImGui::EmToVec2(5.2f, 1.7f)))
            SetCurrentLibraryIndex((int)i);

        if (isSelected)
            ImGui::PopStyleColor();
        ImGui::PopStyleVar();
    }

    ImGui::Spring(0.05f);

    ImGui::PushFont(nullptr, ImGui::GetStyle().FontSizeBase * 1.15f);
    bool showPython = DemoCodeViewer_GetShowPython();
    if (ImGui::RadioButton("C++", !showPython))
        DemoCodeViewer_SetShowPython(false);
    if (ImGui::RadioButton("Python", showPython))
        DemoCodeViewer_SetShowPython(true);
    ImGui::PopFont();

    ImGui::Dummy(HelloImGui::EmToVec2(0.5f, 0.f));

    ImGui::EndHorizontal();
}

// Forward declarations for ImAnim demo windows
void ImAnimDemoBasicsWindow(bool create_window);
void ImAnimDemoWindow(bool create_window);
void ImAnimDocWindow(bool create_window);
void ImAnimUsecaseWindow(bool create_window);

// Show the demo for the current library
// This is called from within a dockable window (always docked to LeftDockSpace)
void ShowCurrentLibraryDemo()
{
    IMGUI_DEMO_MARKER_SHOW_SHORT_INFO();

    const auto& currentLib = GetCurrentLibrary();

    // ImAnim has multiple demos - show them as tabs
    if (currentLib.name == "ImAnim")
    {
        if (ImGui::BeginTabBar("ImAnimDemos"))
        {
            if (ImGui::BeginTabItem("Basics"))
            {
                ImAnimDemoBasicsWindow(false);
                ImGui::EndTabItem();
            }
            if (ImGui::BeginTabItem("Demo"))
            {
                ImAnimDemoWindow(false);
                ImGui::EndTabItem();
            }
            if (ImGui::BeginTabItem("Doc"))
            {
                ImAnimDocWindow(false);
                ImGui::EndTabItem();
            }
            if (ImGui::BeginTabItem("Usecases"))
            {
                ImAnimUsecaseWindow(false);
                ImGui::EndTabItem();
            }
            ImGui::EndTabBar();
        }
    }
    else
    {
        // ImGui, ImPlot, ImPlot3D - show demo content directly (without creating a window)
        if (currentLib.showDemoWindow)
            currentLib.showDemoWindow();
    }
}

std::vector<HelloImGui::DockableWindow> SetupDockableWindows()
{
    // Demo Window (left side, 30%) - content changes based on selected library
    HelloImGui::DockableWindow demoWindow;
    demoWindow.label = "Demo";
    demoWindow.dockSpaceName = "LeftDockSpace";
    demoWindow.imGuiWindowFlags = ImGuiWindowFlags_MenuBar; // we need a menu bar for the ImGui demo window
    demoWindow.GuiFunction = ShowCurrentLibraryDemo;

    // Code Viewer Window (right side, 70%)
    HelloImGui::DockableWindow codeViewerWindow;
    codeViewerWindow.label = "Source Code";
    codeViewerWindow.dockSpaceName = "MainDockSpace";
    codeViewerWindow.GuiFunction = [] { DemoCodeViewer_Show(); };

    return {demoWindow, codeViewerWindow};
}

int main()
{
    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.PostInit = OnPostInit;  // Initialize code viewer after OpenGL init

    runnerParams.appWindowParams.windowGeometry.size = {1400, 900};

    runnerParams.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::ProvideFullScreenDockSpace;

    // Split: Left 30% for demos, Right 70% for code viewer
    HelloImGui::DockingSplit splitLeftRight;
    splitLeftRight.initialDock = "MainDockSpace";
    splitLeftRight.direction = ImGuiDir_Left;
    splitLeftRight.ratio = 0.3f;
    splitLeftRight.newDock = "LeftDockSpace";

    runnerParams.dockingParams.dockingSplits = {splitLeftRight};
    runnerParams.dockingParams.dockableWindows = SetupDockableWindows();

    // Top toolbar for library selection
    HelloImGui::EdgeToolbarOptions toolbarOptions;
    toolbarOptions.sizeEm = 2.3f;
    toolbarOptions.WindowBg = ImVec4(0.3f, 0.3f, 0.3f, 0.9f);
    runnerParams.callbacks.AddEdgeToolbar(
        HelloImGui::EdgeToolbarType::Top,
        ShowLibraryToolbar,
        toolbarOptions
    );

    runnerParams.imGuiWindowParams.showStatusBar = true;
    runnerParams.imGuiWindowParams.showMenuBar = true;

    // Set the app menu
    runnerParams.callbacks.ShowMenus = []
    {
        if (ImGui::BeginMenu("Links"))
        {
            ImGui::SeparatorText("Dear ImGui");
            if (ImGui::MenuItem("Dear ImGui - Github repository"))
                OpenUrl("https://github.com/ocornut/imgui");
            if (ImGui::MenuItem("Dear ImGui - Interactive Manual"))
                OpenUrl("https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html");

            ImGui::SeparatorText("ImPlot");
            if (ImGui::MenuItem("ImPlot - Github repository"))
                OpenUrl("https://github.com/epezent/implot");

            ImGui::SeparatorText("ImPlot3D");
            if (ImGui::MenuItem("ImPlot3D - Github repository"))
                OpenUrl("https://github.com/brenocq/implot3d");

            ImGui::SeparatorText("ImAnim");
            if (ImGui::MenuItem("ImAnim - Github repository"))
                OpenUrl("https://github.com/soufianekhiat/ImAnim");
            if (ImGui::MenuItem("ImAnim - Doc"))
                OpenUrl("https://github.com/soufianekhiat/ImAnim/tree/main/docs");

            ImGui::EndMenu();
        }
    };

    // Add some widgets in the status bar
    runnerParams.callbacks.ShowStatus = [] {
        const auto& lib = GetCurrentLibrary();
        std::string status = "Viewing: " + lib.name + " - Made with [Dear ImGui Bundle](https://github.com/pthom/imgui_bundle/)";
        ImGuiMd::Render(status.c_str());
    };

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
