#include "hello_imgui/hello_imgui.h"
#include "immapp/runner.h"
#include "im_anim.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "demo_code_viewer.h"
#include "imgui_demo_marker_hooks.h"

#include <string>
void OpenUrl(const std::string &url);

// Callback invoked when a demo marker is hovered (with tracking enabled)
void OnDemoMarkerHook(const char* file, int line, const char* section)
{
    (void)section; // unused
    static int last_line = -1;
    if (line == last_line)
        return;
    last_line = line;
    DemoCodeViewer_ShowCodeAt(file, line);
}

void OnBeforeFrame_ImAnimSetup()
{
    // >>> ImAnim frame setup (required every frame) <<<
    iam_update_begin_frame();
    iam_clip_update(ImGui::GetIO().DeltaTime);
}

void OnPostInit()

{
    // Initialize the code viewer (loads source files from assets)
    DemoCodeViewer_Init();

    // Set up the demo marker hook
    GImGuiDemoMarkerHook = OnDemoMarkerHook;
}

std::vector<HelloImGui::DockableWindow> SetupDockableWindows()
{
    // ImAnim Demo Basic Window
    HelloImGui::DockableWindow imAnimDemoBasicsWindow;
    imAnimDemoBasicsWindow.label = "ImAnim Demo - Basics";
    imAnimDemoBasicsWindow.dockSpaceName = "LeftDockSpace";
    imAnimDemoBasicsWindow.GuiFunction = [] {
        IMGUI_DEMO_MARKER_SHOW_SHORT_INFO();
        ImAnimDemoBasicsWindow(false);
    };

    // ImAnim Demo Window
    HelloImGui::DockableWindow imAnimDemoWindow;
    imAnimDemoWindow.label = "ImAnim Demo";
    imAnimDemoWindow.dockSpaceName = "LeftDockSpace";
    imAnimDemoWindow.GuiFunction = [] {
        IMGUI_DEMO_MARKER_SHOW_SHORT_INFO();
        ImAnimDemoWindow(false);
    };

    // ImAnim Documentation Window
    HelloImGui::DockableWindow imAnimDocWindow;
    imAnimDocWindow.label = "ImAnim Doc";
    imAnimDocWindow.dockSpaceName = "LeftDockSpace";
    imAnimDocWindow.GuiFunction = [] {
        IMGUI_DEMO_MARKER_SHOW_SHORT_INFO();
        ImAnimDocWindow(false);
    };

    // ImAnim Usecases Window
    HelloImGui::DockableWindow imAnimUsecaseWindow;
    imAnimUsecaseWindow.label = "ImAnim Usecases";
    imAnimUsecaseWindow.dockSpaceName = "LeftDockSpace";
    imAnimUsecaseWindow.GuiFunction = [] {
        IMGUI_DEMO_MARKER_SHOW_SHORT_INFO();
        ImAnimUsecaseWindow(false);
    };

    // Code Viewer Window (right side, 70%)
    HelloImGui::DockableWindow codeViewerWindow;
    codeViewerWindow.label = "Source Code";
    codeViewerWindow.dockSpaceName = "MainDockSpace";
    codeViewerWindow.GuiFunction = [] { DemoCodeViewer_Show(); };

    return {imAnimDemoBasicsWindow, imAnimDemoWindow, imAnimDocWindow, imAnimUsecaseWindow, codeViewerWindow};
}

int main()
{
    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.PreNewFrame = OnBeforeFrame_ImAnimSetup;  // ImAnim frame setup
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

    runnerParams.imGuiWindowParams.showStatusBar = true;
    runnerParams.imGuiWindowParams.showMenuBar = true;

        // Set the app menu
    runnerParams.callbacks.ShowMenus = []
    {
        if (ImGui::BeginMenu("Links"))
        {
            ImGui::SeparatorText("ImAnim");
            if (ImGui::MenuItem("ImAnim - Github repository"))
                OpenUrl("https://github.com/soufianekhiat/ImAnim");

            if (ImGui::MenuItem("ImAnim - Doc"))
                OpenUrl("https://github.com/soufianekhiat/ImAnim/tree/main/docs");

            ImGui::SeparatorText("Dear ImGui");
            if (ImGui::MenuItem("Dear ImGui - Github repository"))
                OpenUrl("https://github.com/ocornut/imgui");
            if (ImGui::MenuItem("Dear ImGui - Interactive Manual"))
                OpenUrl("https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html");


            // ImGui::SeparatorText("About this manual");
            // if (ImGui::MenuItem("Repository"))
            //     OpenUrl("https://github.com/pthom/imgui_manual");
            ImGui::EndMenu();
        }
    };

    // Add some widgets in the status bar
    runnerParams.callbacks.ShowStatus = [] {
        //MarkdownHelper::Markdown("Dear ImGui Manual - [Repository](https://github.com/pthom/imgui_manual)");
        ImGuiMd::Render("ImAnim Manual, a manual for [ImAnim](https://github.com/soufianekhiat/ImAnim) - Made with [Dear ImGui Bundle](https://github.com/pthom/imgui_bundle/) and [Hello ImGui](https://github.com/pthom/hello_imgui)");
    };

    runnerParams.fpsIdling.fpsIdle = 24.f; // When idling, keep a reasonable framerate

    ImmApp::AddOnsParams addons;
    addons.withMarkdown = true;
    ImmApp::Run(runnerParams, addons);
    return 0;
}
