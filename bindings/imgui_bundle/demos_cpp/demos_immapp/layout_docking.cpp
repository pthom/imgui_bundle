// Docking layouts with Hello ImGui: named dock spaces (DockingSplits), and windows assigned to them
// (DockableWindows). See the Python version (layout_docking.py) for the full explanation.
#include "immapp/immapp.h"
#include <vector>

// ============================================================
// 1. The docking splits: how the screen is divided into named dock spaces
// ============================================================
std::vector<HelloImGui::DockingSplit> CreateDockingSplits()
{
    // "MainDockSpace" (provided automatically) is split into 3 zones:
    //
    //   ┌──────────┬────────────────────┐
    //   │ Command  │                    │
    //   │ Space    │  MainDockSpace     │
    //   │          ├────────────────────┤
    //   │          │  BottomSpace       │
    //   └──────────┴────────────────────┘

    // A "CommandSpace" on the left (25% width)
    HelloImGui::DockingSplit splitLeft;
    splitLeft.initialDock = "MainDockSpace";
    splitLeft.newDock = "CommandSpace";
    splitLeft.direction = ImGuiDir_Left;
    splitLeft.ratio = 0.25f;

    // A "BottomSpace" at the bottom of MainDockSpace (40% height)
    HelloImGui::DockingSplit splitBottom;
    splitBottom.initialDock = "MainDockSpace";
    splitBottom.newDock = "BottomSpace";
    splitBottom.direction = ImGuiDir_Down;
    splitBottom.ratio = 0.4f;

    return {splitLeft, splitBottom};
}

// ============================================================
// 2. The GUI of each dockable window
// ============================================================
float gSliderValue = 0.5f;
int gCounter = 0;
bool gCheckbox = true;

void GuiControls()
{
    ImGui::Text("Sidebar controls");
    ImGui::Separator();
    ImGui::SetNextItemWidth(ImGui::GetContentRegionAvail().x);
    ImGui::SliderFloat("##slider", &gSliderValue, 0.f, 1.f);
    ImGui::Checkbox("Enable", &gCheckbox);
    if (ImGui::Button("Increment"))
    {
        gCounter += 1;
        HelloImGui::Log(HelloImGui::LogLevel::Info, "Counter: %d", gCounter);
    }
    ImGui::Text("Counter: %d", gCounter);
}

void GuiMainView()
{
    ImGui::Text("Main content area");
    ImGui::Separator();
    ImGui::TextWrapped("This window is in 'MainDockSpace'. Try dragging window tabs to rearrange the layout. "
                       "The layout is saved and restored automatically.");
    ImGui::Spacing();
    ImGui::Text("Slider value: %.2f", gSliderValue);
    ImGui::Text("Checkbox: %s", gCheckbox ? "true" : "false");
    ImGui::ProgressBar(gSliderValue);  // a simple progress bar using the slider value
}

void GuiLog()
{
    HelloImGui::LogGui();  // Hello ImGui's built-in log widget
}

void GuiProperties()
{
    ImGui::Text("Properties panel");
    ImGui::Separator();
    ImGui::TextDisabled("This window shares the BottomSpace with 'Log' (see the tabs).");
    ImGui::Spacing();
    ImGui::BulletText("Drag tabs to rearrange");
    ImGui::BulletText("Drag title bar to undock");
    ImGui::BulletText("View > Restore layout to reset");
}

// ============================================================
// 3. The dockable windows: each has a name, a dock space, and a GUI function
// ============================================================
std::vector<HelloImGui::DockableWindow> CreateDockableWindows()
{
    HelloImGui::DockableWindow controls;  // in the left CommandSpace
    controls.label = "Controls";
    controls.dockSpaceName = "CommandSpace";
    controls.GuiFunction = GuiControls;

    HelloImGui::DockableWindow mainView;  // in the center
    mainView.label = "Main View";
    mainView.dockSpaceName = "MainDockSpace";
    mainView.GuiFunction = GuiMainView;

    HelloImGui::DockableWindow log;  // at the bottom
    log.label = "Log";
    log.dockSpaceName = "BottomSpace";
    log.GuiFunction = GuiLog;

    HelloImGui::DockableWindow properties;  // also at the bottom (tabbed with Log)
    properties.label = "Properties";
    properties.dockSpaceName = "BottomSpace";
    properties.GuiFunction = GuiProperties;

    return {controls, mainView, log, properties};
}

// ============================================================
// 4. Main: wire everything together with RunnerParams
// ============================================================
int main()
{
    HelloImGui::RunnerParams params;  // RunnerParams gives full control over the app
    params.appWindowParams.windowTitle = "Docking Layouts";
    params.appWindowParams.windowGeometry.size = {1000, 700};

    // Enable docking
    params.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::ProvideFullScreenDockSpace;

    // Set up the docking layout
    params.dockingParams.dockingSplits = CreateDockingSplits();
    params.dockingParams.dockableWindows = CreateDockableWindows();

    // Reset the layout each time (for a demo)
    params.dockingParams.layoutCondition = HelloImGui::DockingLayoutCondition::ApplicationStart;

    // Enable the "View" menu (to restore the layout)
    params.imGuiWindowParams.showMenuBar = true;

    ImmApp::Run(params);
    return 0;
}
