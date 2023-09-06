/*
A more complex app demo,

It demonstrates:
- How to use a specific application state (instead of using static variables)
- How to set up a complex docking layouts (with several possible layouts):
- How to use the status bar
- How to use default menus (App and view menu), and how to customize them
- How to display a log window
- How to load additional fonts
*/

#include "hello_imgui/hello_imgui.h"
#include "imgui.h"
#include "imgui/misc/cpp/imgui_stdlib.h"
#include "imgui_internal.h"
#include "demo_utils/api_demos.h"

#include <sstream>

//////////////////////////////////////////////////////////////////////////
//    Our Application State
//////////////////////////////////////////////////////////////////////////
struct MyAppSettings
{
    std::string name = "Test";
    int value = 10;
};

struct AppState
{
    float f = 0.0f;
    int counter = 0;

    float rocket_launch_time = 0.f;
    float rocket_progress = 0.0f;

    enum class RocketState {
        Init,
        Preparing,
        Launched
    };
    RocketState rocket_state = RocketState::Init;

    MyAppSettings myAppSettings; // This values will be stored in the application settings
};


//////////////////////////////////////////////////////////////////////////
//    Additional fonts handling
//////////////////////////////////////////////////////////////////////////
ImFont * gTitleFont;
void LoadFonts() // This is called by runnerParams.callbacks.LoadAdditionalFonts
{
    // First, load the default font (the default font should be loaded first)
    HelloImGui::ImGuiDefaultSettings::LoadDefaultFont_WithFontAwesomeIcons();
    // Then load the title font
    gTitleFont = HelloImGui::LoadFontTTF("fonts/DroidSans.ttf", 18.f);
}


//////////////////////////////////////////////////////////////////////////
//    Save additional settings in the ini file
//////////////////////////////////////////////////////////////////////////
// This demonstrates how to store additional info in the application settings
// Use this sparingly!
// This is provided as a convenience only, and it is not intended to store large quantities of text data.

// Warning, the save/load function below are quite simplistic!
std::string MyAppSettingsToString(const MyAppSettings& myAppSettings)
{
    std::stringstream ss;
    ss << myAppSettings.name << "\n";
    ss << myAppSettings.value;
    return ss.str();
}
MyAppSettings StringToMyAppSettings(const std::string& s)
{
    std::stringstream ss(s);
    MyAppSettings myAppSettings;
    ss >> myAppSettings.name;
    ss >> myAppSettings.value;
    return myAppSettings;
}

// Note: LoadUserSettings() and SaveUserSettings() will be called in the callbacks `PostInit` and `BeforeExit`:
//     runnerParams.callbacks.PostInit = [&appState]   { LoadMyAppSettings(appState);};
//     runnerParams.callbacks.BeforeExit = [&appState] { SaveMyAppSettings(appState);};
void LoadMyAppSettings(AppState& appState) //
{
    appState.myAppSettings = StringToMyAppSettings(HelloImGui::LoadUserPref("MyAppSettings"));
}
void SaveMyAppSettings(const AppState& appState)
{
    HelloImGui::SaveUserPref("MyAppSettings", MyAppSettingsToString(appState.myAppSettings));
}

//////////////////////////////////////////////////////////////////////////
//    Gui functions used in this demo
//////////////////////////////////////////////////////////////////////////

// Display a button that will hide the application window
void DemoHideWindow()
{
    ImGui::PushFont(gTitleFont); ImGui::Text("Hide app window"); ImGui::PopFont();
    ImGui::TextWrapped("By clicking the button below, you can hide the window for 3 seconds.");

    static double lastHideTime = -1.;
    if (ImGui::Button("Hide"))
    {
        lastHideTime =  ImGui::GetTime();
        HelloImGui::GetRunnerParams()->appWindowParams.hidden = true;
    }
    if (lastHideTime > 0.)
    {
        double now = ImGui::GetTime();
        if (now - lastHideTime > 3.)
        {
            lastHideTime = -1.;
            HelloImGui::GetRunnerParams()->appWindowParams.hidden = false;
        }
    }
}

// Display a button that will show an additional window
void DemoShowAdditionalWindow()
{
    // Notes:
    //     - it is *not* possible to modify the content of the vector runnerParams.dockingParams.dockableWindows
    //       from the code inside a window's `GuiFunction` (since this GuiFunction will be called while iterating on this vector!)
    //     - there are two ways to dynamically add windows:
    //           * either make them initially invisible, and exclude them from the view menu (such as shown here)
    //           * or modify runnerParams.dockingParams.dockableWindows inside the callback RunnerCallbacks.PreNewFrame
    const char* windowName = "Additional Window";
    ImGui::PushFont(gTitleFont); ImGui::Text("Dynamically add window"); ImGui::PopFont();
    if (ImGui::Button("Show additional window"))
    {
        auto additionalWindowPtr = HelloImGui::GetRunnerParams()->dockingParams.dockableWindowOfName(windowName);
        if (additionalWindowPtr)
        {
            // additionalWindowPtr->includeInViewMenu = true;
            additionalWindowPtr->isVisible = true;
        }
    }
}


void DemoBasicWidgets(AppState& appState)
{
    ImGui::PushFont(gTitleFont); ImGui::Text("Basic widgets demo"); ImGui::PopFont();
    ImGui::TextWrapped("The widgets below will interact with the log window");

    // Edit a float using a slider from 0.0f to 1.0f
    bool changed = ImGui::SliderFloat("float", &appState.f, 0.0f, 1.0f);
    if (changed)
        HelloImGui::Log(HelloImGui::LogLevel::Warning, "state.f was changed to %f", appState.f);

    // Buttons return true when clicked (most widgets return true when edited/activated)
    if (ImGui::Button("Button"))
    {
        appState.counter++;
        HelloImGui::Log(HelloImGui::LogLevel::Info, "Button was pressed");
    }

    ImGui::SameLine();
    ImGui::Text("counter = %d", appState.counter);
}

void DemoUserSettings(AppState& appState)
{
    ImGui::PushFont(gTitleFont); ImGui::Text("User settings"); ImGui::PopFont();
    ImGui::TextWrapped("The values below are stored in the application settings ini file and restored at startup");
    ImGui::SetNextItemWidth(HelloImGui::EmSize(7.f));
    ImGui::InputText("Name", &appState.myAppSettings.name);
    ImGui::SetNextItemWidth(HelloImGui::EmSize(7.f));
    ImGui::SliderInt("Value", &appState.myAppSettings.value, 0, 100);
}

void DemoRocket(AppState& appState)
{
    ImGui::PushFont(gTitleFont); ImGui::Text("Rocket demo"); ImGui::PopFont();
    ImGui::TextWrapped("How to show a progress bar in the status bar");
    if (appState.rocket_state == AppState::RocketState::Init)
    {
        if (ImGui::Button(ICON_FA_ROCKET" Launch rocket"))
        {
            appState.rocket_launch_time = (float)ImGui::GetTime();
            appState.rocket_state = AppState::RocketState::Preparing;
            HelloImGui::Log(HelloImGui::LogLevel::Warning, "Rocket is being prepared");
        }
    }
    else if (appState.rocket_state == AppState::RocketState::Preparing)
    {
        ImGui::Text("Please Wait");
        appState.rocket_progress = (float)(ImGui::GetTime() - appState.rocket_launch_time) / 3.f;
        if (appState.rocket_progress >= 1.0f)
        {
            appState.rocket_state = AppState::RocketState::Launched;
            HelloImGui::Log(HelloImGui::LogLevel::Warning, "Rocket was launched");
        }
    }
    else if (appState.rocket_state == AppState::RocketState::Launched)
    {
        ImGui::Text(ICON_FA_ROCKET " Rocket launched");
        if (ImGui::Button("Reset Rocket"))
        {
            appState.rocket_state = AppState::RocketState::Init;
            appState.rocket_progress = 0.f;
        }
    }
}

void DemoDockingFlags()
{
    ImGui::PushFont(gTitleFont); ImGui::Text("Main dock space node flags"); ImGui::PopFont();
    ImGui::TextWrapped(R"(
This will edit the ImGuiDockNodeFlags for "MainDockSpace".
Most flags are inherited by children dock spaces.
    )");
    struct DockFlagWithInfo {
        ImGuiDockNodeFlags flag;
        std::string label;
        std::string tip;
    };
    std::vector<DockFlagWithInfo> all_flags = {
        {ImGuiDockNodeFlags_NoSplit, "NoSplit", "prevent Dock Nodes from being split"},
        {ImGuiDockNodeFlags_NoResize, "NoResize", "prevent Dock Nodes from being resized"},
        {ImGuiDockNodeFlags_AutoHideTabBar, "AutoHideTabBar",
         "show tab bar only if multiple windows\n"
         "You will need to restore the layout after changing (Menu \"View/Restore Layout\")"},
        {ImGuiDockNodeFlags_NoDockingInCentralNode, "NoDockingInCentralNode",
         "prevent docking in central node\n"
         "(only works with the main dock space)"},
        // {ImGuiDockNodeFlags_PassthruCentralNode, "PassthruCentralNode", "advanced"},
    };
    auto & mainDockSpaceNodeFlags = HelloImGui::GetRunnerParams()->dockingParams.mainDockSpaceNodeFlags;
    for (auto flag: all_flags)
    {
        ImGui::CheckboxFlags(flag.label.c_str(), &mainDockSpaceNodeFlags, flag.flag);
        if (ImGui::IsItemHovered())
            ImGui::SetTooltip("%s", flag.tip.c_str());
    }
}

void GuiWindowLayoutCustomization()
{
    ImGui::PushFont(gTitleFont); ImGui::Text("Switch between layouts"); ImGui::PopFont();
    ImGui::Text("with the menu \"View/Layouts\"");
    if (ImGui::IsItemHovered())
        ImGui::SetTooltip("Each layout remembers separately the modifications applied by the user, \nand the selected layout is restored at startup");
    ImGui::Separator();
    ImGui::PushFont(gTitleFont); ImGui::Text("Change the theme"); ImGui::PopFont();
    ImGui::Text("with the menu \"View/Theme\"");
    if (ImGui::IsItemHovered())
        ImGui::SetTooltip("The selected theme is remembered and restored at startup");
    ImGui::Separator();
    DemoDockingFlags();
    ImGui::Separator();
}

void GuiWindowDemoFeatures(AppState& appState)
{
    DemoBasicWidgets(appState);
    ImGui::Separator();
    DemoRocket(appState);
    ImGui::Separator();
    DemoUserSettings(appState);
    ImGui::Separator();
    DemoHideWindow();
    ImGui::Separator();
    DemoShowAdditionalWindow();
    ImGui::Separator();
}

// The Gui of the status bar
void StatusBarGui(AppState& app_state)
{
    if (app_state.rocket_state == AppState::RocketState::Preparing)
    {
        ImGui::Text("Rocket completion: ");
        ImGui::SameLine();
        ImGui::ProgressBar(app_state.rocket_progress, HelloImGui::EmToVec2(7.0f, 1.0f));
    }
}

// The menu gui
void ShowMenuGui()
{
    if (ImGui::BeginMenu("My Menu"))
    {
        bool clicked = ImGui::MenuItem("Test me", "", false);
        if (clicked)
        {
            HelloImGui::Log(HelloImGui::LogLevel::Warning, "It works");
        }
        ImGui::EndMenu();
    }
}

void ShowAppMenuItems()
{
    if (ImGui::MenuItem("A Custom app menu item"))
        HelloImGui::Log(HelloImGui::LogLevel::Info, "Clicked on A Custom app menu item");
}


//////////////////////////////////////////////////////////////////////////
//    Docking Layouts and Docking windows
//////////////////////////////////////////////////////////////////////////

//
// 1. Define the Docking splits (two versions are available)
//
std::vector<HelloImGui::DockingSplit> CreateDefaultDockingSplits()
{
    //    Define the default docking splits,
    //    i.e. the way the screen space is split in different target zones for the dockable windows
    //     We want to split "MainDockSpace" (which is provided automatically) into three zones, like this:
    //
    //    ___________________________________________
    //    |        |                                |
    //    | Command|                                |
    //    | Space  |    MainDockSpace               |
    //    |        |                                |
    //    |        |                                |
    //    |        |                                |
    //    -------------------------------------------
    //    |     MiscSpace                           |
    //    -------------------------------------------
    //

    // Then, add a space named "MiscSpace" whose height is 25% of the app height.
    // This will split the preexisting default dockspace "MainDockSpace" in two parts.
    HelloImGui::DockingSplit splitMainMisc;
    splitMainMisc.initialDock = "MainDockSpace";
    splitMainMisc.newDock = "MiscSpace";
    splitMainMisc.direction = ImGuiDir_Down;
    splitMainMisc.ratio = 0.25f;

    // Then, add a space to the left which occupies a column whose width is 25% of the app width
    HelloImGui::DockingSplit splitMainCommand;
    splitMainCommand.initialDock = "MainDockSpace";
    splitMainCommand.newDock = "CommandSpace";
    splitMainCommand.direction = ImGuiDir_Left;
    splitMainCommand.ratio = 0.25f;

    std::vector<HelloImGui::DockingSplit> splits {splitMainMisc, splitMainCommand};
    return splits;
}

std::vector<HelloImGui::DockingSplit> CreateAlternativeDockingSplits()
{
    //    Define alternative docking splits for the "Alternative Layout"
    //    ___________________________________________
    //    |                |                        |
    //    | Misc           |                        |
    //    | Space          |    MainDockSpace       |
    //    |                |                        |
    //    -------------------------------------------
    //    |                                         |
    //    |                                         |
    //    |     CommandSpace                        |
    //    |                                         |
    //    -------------------------------------------

    HelloImGui::DockingSplit splitMainCommand;
    splitMainCommand.initialDock = "MainDockSpace";
    splitMainCommand.newDock = "CommandSpace";
    splitMainCommand.direction = ImGuiDir_Down;
    splitMainCommand.ratio = 0.5f;

    HelloImGui::DockingSplit splitMainMisc;
    splitMainMisc.initialDock = "MainDockSpace";
    splitMainMisc.newDock = "MiscSpace";
    splitMainMisc.direction = ImGuiDir_Left;
    splitMainMisc.ratio = 0.5f;

    std::vector<HelloImGui::DockingSplit> splits {splitMainCommand, splitMainMisc};
    return splits;
}

//
// 2. Define the Dockable windows
//
std::vector<HelloImGui::DockableWindow> CreateDockableWindows(AppState& appState)
{
    // A window named "FeaturesDemo" will be placed in "CommandSpace". Its Gui is provided by "GuiWindowDemoFeatures"
    HelloImGui::DockableWindow featuresDemoWindow;
    featuresDemoWindow.label = "Features Demo";
    featuresDemoWindow.dockSpaceName = "CommandSpace";
    featuresDemoWindow.GuiFunction = [&] { GuiWindowDemoFeatures(appState); };

    // A layout customization window will be placed in "MainDockSpace". Its Gui is provided by "GuiWindowLayoutCustomization"
    HelloImGui::DockableWindow layoutCustomizationWindow;
    layoutCustomizationWindow.label = "Layout customization";
    layoutCustomizationWindow.dockSpaceName = "MainDockSpace";
    layoutCustomizationWindow.GuiFunction = GuiWindowLayoutCustomization;

    // A Log window named "Logs" will be placed in "MiscSpace". It uses the HelloImGui logger gui
    HelloImGui::DockableWindow logsWindow;
    logsWindow.label = "Logs";
    logsWindow.dockSpaceName = "MiscSpace";
    logsWindow.GuiFunction = [] { HelloImGui::LogGui(); };

    // A Window named "Dear ImGui Demo" will be placed in "MainDockSpace"
    HelloImGui::DockableWindow dearImGuiDemoWindow;
    dearImGuiDemoWindow.label = "Dear ImGui Demo";
    dearImGuiDemoWindow.dockSpaceName = "MainDockSpace";
    dearImGuiDemoWindow.GuiFunction = [] { ImGui::ShowDemoWindow(); };

    // additionalWindow is initially not visible (and not mentioned in the view menu).
    // it will be opened only if the user chooses to display it
    HelloImGui::DockableWindow additionalWindow;
    additionalWindow.label = "Additional Window";
    additionalWindow.isVisible = false;               // this window is initially hidden,
    additionalWindow.includeInViewMenu = false;       // it is not shown in the view menu,
    additionalWindow.rememberIsVisible = false;       // its visibility is not saved in the settings file,
    additionalWindow.dockSpaceName = "MiscSpace";     // when shown, it will appear in MiscSpace.
    additionalWindow.GuiFunction = [] { ImGui::Text("This is the additional window"); };

    std::vector<HelloImGui::DockableWindow> dockableWindows {
        featuresDemoWindow,
        layoutCustomizationWindow,
        logsWindow,
        dearImGuiDemoWindow,
        additionalWindow,
    };
    return dockableWindows;
};

//
// 3. Define the layouts:
//        A layout is stored inside DockingParams, and stores the splits + the dockable windows.
//        Here, we provide the default layout, and two alternative layouts.
//
HelloImGui::DockingParams CreateDefaultLayout(AppState& appState)
{
    HelloImGui::DockingParams dockingParams;
    // dockingParams.layoutName = "Default"; // By default, the layout name is already "Default"
    dockingParams.dockingSplits = CreateDefaultDockingSplits();
    dockingParams.dockableWindows = CreateDockableWindows(appState);
    return dockingParams;
}

std::vector<HelloImGui::DockingParams> CreateAlternativeLayouts(AppState& appState)
{
    HelloImGui::DockingParams alternativeLayout;
    {
        alternativeLayout.layoutName = "Alternative Layout";
        alternativeLayout.dockingSplits = CreateAlternativeDockingSplits();
        alternativeLayout.dockableWindows = CreateDockableWindows(appState);
    }
    HelloImGui::DockingParams tabsLayout;
    {
        tabsLayout.layoutName = "Tabs Layout";
        tabsLayout.dockableWindows = CreateDockableWindows(appState);
        // Force all windows to be presented in the MainDockSpace
        for (auto& window: tabsLayout.dockableWindows)
            window.dockSpaceName = "MainDockSpace";
        // In "Tabs Layout", no split is created
        tabsLayout.dockingSplits = {};
    }
    return {alternativeLayout, tabsLayout};
};


//////////////////////////////////////////////////////////////////////////
//    main(): here, we simply fill RunnerParams, then run the application
//////////////////////////////////////////////////////////////////////////
int main(int, char**)
{
    ChdirBesideAssetsFolder();

    //###############################################################################################
    // Part 1: Define the application state, fill the status and menu bars, and load additional font
    //###############################################################################################

    // Our application state
    AppState appState;

    // Hello ImGui params (they hold the settings as well as the Gui callbacks)
    HelloImGui::RunnerParams runnerParams;

    // Note: by setting the window title, we also set the name of the ini files in which the settings for the user
    // layout will be stored: Docking_demo.ini
    runnerParams.appWindowParams.windowTitle = "Docking demo";

    runnerParams.imGuiWindowParams.menuAppTitle = "Docking App";
    runnerParams.appWindowParams.windowGeometry.size = {1000, 900};
    runnerParams.appWindowParams.restorePreviousGeometry = true;

    // Set LoadAdditionalFonts callback
    runnerParams.callbacks.LoadAdditionalFonts = LoadFonts;

    //
    // Status bar
    //
    // We use the default status bar of Hello ImGui
    runnerParams.imGuiWindowParams.showStatusBar = true;
    // Add custom widgets in the status bar
    runnerParams.callbacks.ShowStatus = [&appState]() { StatusBarGui(appState); };
    // uncomment next line in order to hide the FPS in the status bar
    // runnerParams.imGuiWindowParams.showStatusFps = false;

    //
    // Menu bar
    //
    runnerParams.imGuiWindowParams.showMenuBar = true;          // We use the default menu of Hello ImGui
    // fill callbacks ShowMenuGui and ShowAppMenuItems, to add items to the default menu and to the App menu
    runnerParams.callbacks.ShowMenus = ShowMenuGui;
    runnerParams.callbacks.ShowAppMenuItems = ShowAppMenuItems;

    //
    // Load user settings at callbacks `PostInit` and save them at `BeforeExit`
    //
    runnerParams.callbacks.PostInit = [&appState]   { LoadMyAppSettings(appState);};
    runnerParams.callbacks.BeforeExit = [&appState] { SaveMyAppSettings(appState);};

    //###############################################################################################
    // Part 2: Define the application layout and windows
    //###############################################################################################

    // First, tell HelloImGui that we want full screen dock space (this will create "MainDockSpace")
    runnerParams.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::ProvideFullScreenDockSpace;
    // In this demo, we also demonstrate multiple viewports: you can drag windows outside out the main window in order to put their content into new native windows
    runnerParams.imGuiWindowParams.enableViewports = true;
    // Set the default layout (this contains the default DockingSplits and DockableWindows)
    runnerParams.dockingParams = CreateDefaultLayout(appState);
    // Add alternative layouts
    runnerParams.alternativeDockingLayouts = CreateAlternativeLayouts(appState);

    // uncomment the next line if you want to always start with the layout defined in the code
    //     (otherwise, modifications to the layout applied by the user layout will be remembered)
    // runnerParams.dockingParams.layoutCondition = HelloImGui::DockingLayoutCondition::ApplicationStart;

    //###############################################################################################
    // Part 3: Run the app
    //###############################################################################################
    HelloImGui::Run(runnerParams); // Note: with ImGuiBundle, it is also possible to use ImmApp::Run(...)


    return 0;
}
