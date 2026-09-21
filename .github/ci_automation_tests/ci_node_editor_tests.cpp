// Runner for the tests of imgui-node-editor (external/imgui-node-editor/imgui-node-editor/tests)
//    ci_node_editor_tests          interactive: look at the scene, launch the tests from the test engine window
//    ci_node_editor_tests --auto   run all the tests, then exit (exit code 0 if they all passed)
//    ci_node_editor_tests --auto layout_combo   same, with a filter on the test names
#ifdef HELLOIMGUI_WITH_TEST_ENGINE
#include "hello_imgui/hello_imgui.h"
#include "imgui_test_engine/imgui_te_engine.h"
#include "imgui_test_engine/imgui_te_ui.h"
#include "node_editor_tests.h"

#include <cstdio>
#include <cstring>


static bool gAutoMode = false;
static const char* gTestFilter = "node_editor";
static bool gTestsQueued = false;
static int gCountTested = 0, gCountSuccess = 0;


// In auto mode: queue all the tests once the app is settled, exit when they are done
static void AutoModeUpdate()
{
    ImGuiTestEngine* engine = HelloImGui::GetImGuiTestEngine();
    if (!gTestsQueued)
    {
        if (ImGui::GetFrameCount() < 3)
            return;
        ImGuiTestEngine_GetIO(engine).ConfigLogToTTY = true;  // so that a failure can be read in the CI log
        ImGuiTestEngine_QueueTests(engine, ImGuiTestGroup_Tests, gTestFilter);
        gTestsQueued = true;
    }
    else if (ImGuiTestEngine_IsTestQueueEmpty(engine))
    {
        ImGuiTestEngineResultSummary summary;
        ImGuiTestEngine_GetResultSummary(engine, &summary);
        gCountTested = summary.CountTested;
        gCountSuccess = summary.CountSuccess;
        HelloImGui::GetRunnerParams()->appShallExit = true;
    }
}


static void Gui()
{
    NodeEditorTests_ShowGui();
    ImGuiTestEngine_ShowTestEngineWindows(HelloImGui::GetImGuiTestEngine(), NULL);
    if (gAutoMode)
        AutoModeUpdate();
}


int main(int argc, char** argv)
{
    gAutoMode = (argc > 1) && (strcmp(argv[1], "--auto") == 0);
    if (gAutoMode && argc > 2)
        gTestFilter = argv[2];

    HelloImGui::RunnerParams runnerParams;
    runnerParams.appWindowParams.windowTitle = "imgui-node-editor tests";
    runnerParams.appWindowParams.windowGeometry.size = {1400, 900};
    runnerParams.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::NoDefaultWindow;
    runnerParams.iniDisable = true;
    runnerParams.useImGuiTestEngine = true;
    runnerParams.callbacks.ShowGui = Gui;
    runnerParams.callbacks.RegisterTests = []() { NodeEditorTests_Register(HelloImGui::GetImGuiTestEngine()); };
    runnerParams.callbacks.BeforeExit = NodeEditorTests_Shutdown;
    HelloImGui::Run(runnerParams);

    if (!gAutoMode)
        return 0;
    printf("node_editor tests: %d / %d passed\n", gCountSuccess, gCountTested);
    return (gCountTested > 0 && gCountSuccess == gCountTested) ? 0 : 1;
}
#else // HELLOIMGUI_WITH_TEST_ENGINE
#include <cstdio>
int main() {
    fprintf(stderr, "This app is not built with HELLOIMGUI_WITH_TEST_ENGINE\n");
}
#endif // HELLOIMGUI_WITH_TEST_ENGINE
