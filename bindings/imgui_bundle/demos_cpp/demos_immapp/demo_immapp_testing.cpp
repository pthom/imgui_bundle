// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// demo_immapp_testing: easy automated tests with `ImmApp::Testing`, a thin layer on the test engine:
// a test function drives the app and captures screenshots, then the app exits.
// The same recipe gives documentation pictures, and lets an AI agent see and drive the app it writes.

// Customization: edit EXIT_AFTER_TESTS. The screenshots go to a temporary folder, printed at the end of the test.
#ifdef HELLOIMGUI_WITH_TEST_ENGINE

#include "imgui.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui_test_engine/imgui_te_engine.h"
#include "imgui_test_engine/imgui_te_context.h"
#include "immapp/testing.h"

#include <cstdio>
#include <filesystem>
#include <string>

static const std::string SCREENSHOTS_FOLDER =  // where the screenshots go
    (std::filesystem::temp_directory_path() / "demo_immapp_testing").string();
static const bool        EXIT_AFTER_TESTS   = true;


struct State
{
    int  counter     = 0;
    int  sliderValue = 0;
    bool checkbox    = false;
};
static State gState;


static void Gui()
{
    ImGui::Text("demo_immapp_testing: exercise these widgets under the test engine");
    ImGui::Separator();

    if (ImGui::Button("Click me"))
        gState.counter++;
    ImGui::SameLine();
    ImGui::Text("clicks: %d", gState.counter);

    ImGui::SliderInt("A slider", &gState.sliderValue, 0, 100);
    ImGui::Checkbox("A checkbox", &gState.checkbox);

    if (ImGui::CollapsingHeader("Details"))
    {
        ImGui::Text("These details are hidden until the header is expanded.");
        ImGui::BulletText("Line 1");
        ImGui::BulletText("Line 2");
    }
}


static bool gTestDone = false;


static void ScreenshotTest(ImGuiTestContext* ctx)
{
    std::filesystem::create_directories(SCREENSHOTS_FOLDER);
    ImmApp::Testing::Capture(ctx, SCREENSHOTS_FOLDER + "/00_initial.png");

    ctx->ItemClick("//**/Click me");
    ctx->ItemClick("//**/Click me");
    ImmApp::Testing::Capture(ctx, SCREENSHOTS_FOLDER + "/01_after_clicks.png");

    ctx->ItemInputValue("//**/A slider", 77);
    ImmApp::Testing::Capture(ctx, SCREENSHOTS_FOLDER + "/02_slider.png");

    ctx->ItemClick("//**/A checkbox");
    ImmApp::Testing::Capture(ctx, SCREENSHOTS_FOLDER + "/03_checkbox.png");

    ctx->ItemOpen("//**/Details");
    ImmApp::Testing::Capture(ctx, SCREENSHOTS_FOLDER + "/04_details.png");
    std::printf("Wrote 5 PNGs to %s\n", SCREENSHOTS_FOLDER.c_str());

    gTestDone = true;
}


int main(int, char**)
{
    gState = State();  // reset so repeated runs stay deterministic

    HelloImGui::RunnerParams params;
    params.appWindowParams.windowTitle       = "demo_immapp_testing";
    params.appWindowParams.windowGeometry.size = {600, 400};
    params.iniDisable                        = true;
    params.useImGuiTestEngine                = true;
    params.callbacks.ShowGui                 = Gui;

    params.callbacks.RegisterTests = []()
    {
        ImGuiTestEngine* engine = HelloImGui::GetImGuiTestEngine();
        ImGuiTestEngine_GetIO(engine).ConfigRunSpeed = ImGuiTestRunSpeed_Normal;

        ImGuiTest* test = IM_REGISTER_TEST(engine, "demo_immapp_testing", "screenshots");
        test->TestFunc = ScreenshotTest;
        ImGuiTestEngine_QueueTest(engine, test);
    };

    if (EXIT_AFTER_TESTS)
    {
        params.callbacks.BeforeImGuiRender = []()
        {
            if (!gTestDone)
                return;
            ImGuiTestEngine* engine = HelloImGui::GetImGuiTestEngine();
            if (ImGuiTestEngine_IsTestQueueEmpty(engine))
                HelloImGui::GetRunnerParams()->appShallExit = true;
        };
    }

    HelloImGui::Run(params);
    return 0;
}

#else // HELLOIMGUI_WITH_TEST_ENGINE
int main(int, char**) { return 0; }
#endif
