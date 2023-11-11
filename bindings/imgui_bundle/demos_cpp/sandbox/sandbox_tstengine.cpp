#ifdef IMGUI_BUNDLE_WITH_TEST_ENGINE
#include "imgui.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui_test_engine/imgui_te_ui.h"
#include "imgui_test_engine/imgui_te_engine.h"
#include "imgui_test_engine/imgui_te_context.h"


ImGuiTest *test_open_metric, *test_capture_screenshot;


void MyRegisterTests()
{
    auto engine = HelloImGui::GetImGuiTestEngine();

    //-----------------------------------------------------------------
    // ## Open Metrics window
    //-----------------------------------------------------------------

    test_open_metric = IM_REGISTER_TEST(engine, "demo_tests", "open_metrics");
    test_open_metric->TestFunc = [](ImGuiTestContext* ctx)
    {
        ctx->SetRef("Dear ImGui Demo");
        ctx->MenuCheck("Tools/Metrics\\/Debugger");
    };

    //-----------------------------------------------------------------
    // ## Capture entire Dear ImGui Demo window.
    //-----------------------------------------------------------------

    test_capture_screenshot = IM_REGISTER_TEST(engine, "demo_tests", "capture_screenshot");
    test_capture_screenshot->TestFunc = [](ImGuiTestContext* ctx)
    {
        ctx->SetRef("Dear ImGui Demo");
        ctx->ItemOpen("Widgets");       // Open collapsing header
        ctx->ItemOpenAll("Basic");      // Open tree node and all its descendant
        ctx->CaptureScreenshotWindow("Dear ImGui Demo", ImGuiCaptureFlags_StitchAll | ImGuiCaptureFlags_HideMouseCursor);
    };

}

void AppGui()
{
    auto engine = HelloImGui::GetImGuiTestEngine();
    ImGui::ShowDemoWindow();
    ImGuiTestEngine_ShowTestEngineWindows(engine, NULL);

    if (ImGui::Button("Run open metric automation"))
        ImGuiTestEngine_QueueTest(engine, test_open_metric);
    if (ImGui::Button("Run capture screenshot automation"))
        ImGuiTestEngine_QueueTest(engine, test_capture_screenshot);
}


int main(int, char**)
{
    HelloImGui::RunnerParams runnerParams;
    runnerParams.useImGuiTestEngine = true;

    runnerParams.callbacks.ShowGui = AppGui;
    runnerParams.callbacks.RegisterTests = MyRegisterTests;
    HelloImGui::Run(runnerParams);
}

#else // #ifdef IMGUI_BUNDLE_WITH_TEST_ENGINE
int main(int, char**) {}
#endif
