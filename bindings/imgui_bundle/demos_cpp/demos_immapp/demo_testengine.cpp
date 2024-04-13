// A demo app that demonstrates how to use ImGui Test Engine (https://github.com/ocornut/imgui_test_engine)
//
// It demonstrates how to:
// - enable ImGui Test Engine via runnerParams.useImGuiTestEngine
// - define a callback where the tests are registered (runnerParams.callbacks.RegisterTests)
// - create tests, and:
//   - automate actions using "named references" (see https://github.com/ocornut/imgui_test_engine/wiki/Named-References)
//   - display an optional custom GUI for a test
//   - manipulate custom variables
//   - check that simulated actions do modify those variables
//
// Important note: ImGui Test Engine falls under the Dear ImGui Test Engine License
//    See: https://github.com/ocornut/imgui_test_engine/blob/main/imgui_test_engine/LICENSE.txt
//    TL;DR: free for individuals, educational, open-source and small businesses uses.
//           Paid for larger businesses. Read license for details.
//           License sales to larger businesses are used to fund and sustain the development of Dear ImGui.

#include "immapp/immapp.h"
#include "imgui.h"
#include "imgui_test_engine/imgui_te_engine.h"
#include "imgui_test_engine/imgui_te_context.h"
#include "imgui_test_engine/imgui_te_ui.h"


#include <vector>

// Our tests, that will automate the application
ImGuiTest* testOpenPopup;
ImGuiTest* testCaptureScreenshot;
ImGuiTest* testCustomGui;

bool gShowStackToolWindow = false;
int nbAltA = 0;


// This function is called at startup and will instantiate the tests
void MyRegisterTests()
{
    ImGuiTestEngine* engine = HelloImGui::GetImGuiTestEngine();

    // Demo 1: Open popup
    testOpenPopup = IM_REGISTER_TEST(engine, "Demo Tests", "Open Popup");
    auto testOpenPopupFunc = [](ImGuiTestContext* ctx) {
        // This is the function that will be called by our test
        ctx->SetRef("Dear ImGui Demo");              // From now on, all actions happen in the "Dear ImGui Demo" window
        ctx->ItemOpen("**/Popups & Modal windows");     // Open the "Popups & Modal windows" tree item
        ctx->ItemOpen("**/Modals");                     // Open the "Modal" tree item
        ctx->ItemClick("**/Delete..");               // Click the "Delete.." button ("**" means: search inside children)
        ctx->ItemClick("//Delete?/Cancel");          // Click the "Cancel" button:
        //    here, "//"  means "ignore previous set_ref" and search
        //    for the cancel button in the root popup window named "Delete?"
        ctx->ItemClose("**/Popups & Modal windows");    // Close the "Popups & Modal windows" tree item
    };
    // Let the test call our function
    testOpenPopup->TestFunc = testOpenPopupFunc;

    // Demo 2: Capture Dear ImGui Demo window
    testCaptureScreenshot = IM_REGISTER_TEST(engine, "Demo Tests", "Capture Screenshot");
    auto testCaptureScreenshotFunc = [](ImGuiTestContext* ctx)
    {
        ctx->SetRef("Dear ImGui Demo");                   // From now on, actions happen in the "Dear ImGui Demo" window
        ctx->ItemOpen("**/Widgets");                         // Open the "Widgets", then "Basic" tree item
        ctx->ItemOpenAll("**/Basic");
        ctx->CaptureScreenshotWindow("Dear ImGui Demo"); // Capture window and save screenshot
        ctx->ItemClose("**/Widgets");
    };
    testCaptureScreenshot->TestFunc = testCaptureScreenshotFunc;

    // Demo 3: a test with a custom GUI and custom variables
    // which asserts that simulated actions successfully changed the variables values
    testCustomGui = IM_REGISTER_TEST(engine, "Demo Tests", "Test custom GUI & vars");
    // Our custom variables container
    struct TestVar2 {
        int myInt = 42;
    };
    testCustomGui->SetVarsDataType<TestVar2>();
    auto testCustomGuiFunc = [](ImGuiTestContext* ctx)
    {
        // Custom GUI for this test: it can edit our custom variable
        TestVar2& vars = ctx->GetVars<TestVar2>();
        ImGui::SetNextWindowSize(HelloImGui::EmToVec2(40, 8));
        ImGui::Begin("Custom Gui Test Window", nullptr, ImGuiWindowFlags_NoSavedSettings);
        ImGui::SliderInt("Slider", &vars.myInt, 0, 1000);
        ImGui::End();
    };
    auto testWithVarsTestFunc = [](ImGuiTestContext* ctx){
        // Our test, that will perform actions in the custom GUI, and assert that actions do change the custom variables
        TestVar2& vars = ctx->GetVars<TestVar2>();
        ctx->SetRef("Custom Gui Test Window");
        IM_CHECK_EQ(vars.myInt, 42);
        ctx->ItemInputValue("Slider", 123);
        IM_CHECK_EQ(vars.myInt, 123);
    };
    // Let the test call our test function, and also call our custom GUI
    testCustomGui->TestFunc = testWithVarsTestFunc;
    testCustomGui->GuiFunc = testCustomGuiFunc;

    // Demo 4: Write to text field
    auto testWrite = IM_REGISTER_TEST(engine, "Demo Tests", "Write to text field");
    auto testWriteFunc = [](ImGuiTestContext* ctx)
    {
        ctx->SetRef("Dear ImGui Demo");
        ctx->ItemOpen("**/Widgets");
        ctx->ItemOpen("**/Text Input");
        ctx->ItemOpen("**/Multi-line Text Input");
        ctx->ItemClick("**/##source");
        ctx->KeyChars("Hello from test engine!");
        // Note: ctx.KeyUp/Down/Press also send events that you can process in the GUI
        //       However, you need to use KeyChars to input text in the text widgets
    };
    testWrite->TestFunc = testWriteFunc;

    // Demo 5: Press Alt+A
    auto testAltA = IM_REGISTER_TEST(engine, "Demo Tests", "Test key combination (Alt-A)");
    auto testAltAFunc = [](ImGuiTestContext* ctx)
    {
        ctx->KeyDown(ImGuiKey_LeftAlt);
        ctx->KeyDown(ImGuiKey_A);
        ctx->KeyUp(ImGuiKey_A);
        ctx->KeyUp(ImGuiKey_LeftAlt);
    };
    testAltA->TestFunc = testAltAFunc;
}


// Our application GUI: shows that we can trigger the test manually
void MyGui()
{
    ImGui::Checkbox("Show ID Stack Tool Window", &gShowStackToolWindow);
    if (ImGui::IsItemHovered())
        ImGui::SetTooltip("This tool window can help to identify the ID of the widgets (use \"Copy path to clipboard\")");
    if (gShowStackToolWindow)
        ImGui::ShowIDStackToolWindow();

    ImGuiTestEngine* testEngine = HelloImGui::GetImGuiTestEngine();
    if (ImGui::Button("Run \"Open popup\""))
        ImGuiTestEngine_QueueTest(testEngine, testOpenPopup);
    if (ImGui::Button("Run \"Capture Screenshot\""))
        ImGuiTestEngine_QueueTest(testEngine, testCaptureScreenshot);
    if (ImGui::Button("Run \"Test custom GUI & vars\""))
        ImGuiTestEngine_QueueTest(testEngine, testCustomGui);

    ImGuiTestEngineIO& engineIo = ImGuiTestEngine_GetIO(testEngine);
    ImGui::Text("Speed:");
    ImGui::SameLine();
    if (ImGui::Button("Fast"))
        engineIo.ConfigRunSpeed = ImGuiTestRunSpeed_Fast;
    ImGui::SameLine();
    if (ImGui::Button("Normal"))
        engineIo.ConfigRunSpeed = ImGuiTestRunSpeed_Normal;
    ImGui::SameLine();
    if (ImGui::Button("Cinematic"))
        engineIo.ConfigRunSpeed = ImGuiTestRunSpeed_Cinematic;

    if (ImGui::IsKeyPressed(ImGuiKey_A) && ImGui::IsKeyDown(ImGuiKey_LeftAlt))
        nbAltA++;
    if (nbAltA > 0)
        ImGui::Text("Alt-A combination was pressed");
}

// Defined later: helps to define the application layout, display the ImGui Demo, & ImGui Test Engine Window
void ApplyApplicationLayout(HelloImGui::RunnerParams* runnerParams);


// Our main function, where we need to:
// - instantiate RunnerParams
// - set `runnerParams.useImGuiTestEngine = true`
// - fill `runnerParams.callbacks.registerTests`
int main(int, const char**)
{
    // Instantiate RunnerParams
    HelloImGui::RunnerParams runnerParams;

    // Apply the application layout configuration
    ApplyApplicationLayout(&runnerParams);

    // Enable ImGui Test Engine
    runnerParams.useImGuiTestEngine = true;

    // Set the test registration function
    runnerParams.callbacks.RegisterTests = MyRegisterTests;

    // Run the ImGui application
    HelloImGui::Run(runnerParams);
}


///////////////////////////////////////////////////////////////////////////////
// End of demo code
///////////////////////////////////////////////////////////////////////////////


// Define the default docking splits for the application layout
std::vector<HelloImGui::DockingSplit> CreateDefaultDockingSplits()
{
    // Define the application layout: split the window into 3 spaces
    HelloImGui::DockingSplit splitMainDemo;
    splitMainDemo.initialDock = "MainDockSpace";
    splitMainDemo.newDock = "ImGuiDemoSpace";
    splitMainDemo.direction = ImGuiDir_Right;
    splitMainDemo.ratio = 0.5f;

    HelloImGui::DockingSplit splitMainTest;
    splitMainTest.initialDock = "MainDockSpace";
    splitMainTest.newDock = "TestEngineSpace";
    splitMainTest.direction = ImGuiDir_Down;
    splitMainTest.ratio = 0.7f;

    return {splitMainDemo, splitMainTest};
}

// Define the dockable windows for the application layout
std::vector<HelloImGui::DockableWindow> CreateDockableWindows()
{
    // Define the app windows: MyGui, ImGui Demo Window, Dear ImGui Test Engine
    HelloImGui::DockableWindow myWindow;
    myWindow.label = "Run Demos";
    myWindow.dockSpaceName = "MainDockSpace";
    myWindow.GuiFunction = &MyGui;

    HelloImGui::DockableWindow dearImGuiDemoWindow;
    dearImGuiDemoWindow.label = "Dear ImGui Demo";
    dearImGuiDemoWindow.dockSpaceName = "ImGuiDemoSpace";
    dearImGuiDemoWindow.GuiFunction = []() { ImGui::ShowDemoWindow(); };

    HelloImGui::DockableWindow testEngineWindow;
    testEngineWindow.label = "Dear ImGui Test Engine";
    testEngineWindow.dockSpaceName = "TestEngineSpace";
    testEngineWindow.GuiFunction = []() { ImGuiTestEngine_ShowTestEngineWindows(HelloImGui::GetImGuiTestEngine(), nullptr); };

    return {myWindow, dearImGuiDemoWindow, testEngineWindow};
}


// Apply the application layout and windows to the runner parameters
void ApplyApplicationLayout(HelloImGui::RunnerParams* runnerParams)
{
    // Define the application layout and windows
    runnerParams->appWindowParams.windowTitle = "Demo ImGui Test Engine";
    runnerParams->imGuiWindowParams.defaultImGuiWindowType =
        HelloImGui::DefaultImGuiWindowType::ProvideFullScreenDockSpace;
    runnerParams->dockingParams.dockingSplits = CreateDefaultDockingSplits();
    runnerParams->dockingParams.dockableWindows = CreateDockableWindows();
    runnerParams->dockingParams.layoutCondition = HelloImGui::DockingLayoutCondition::ApplicationStart;
}
