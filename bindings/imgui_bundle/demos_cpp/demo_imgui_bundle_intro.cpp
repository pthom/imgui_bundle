// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/hello_imgui.h"
#include "immapp/browse_to_url.h"
#include "demo_utils/animate_logo.h"

#ifdef HELLOIMGUI_WITH_TEST_ENGINE
#include "imgui_test_engine/imgui_te_engine.h"
#include "imgui_test_engine/imgui_te_context.h"
#include "imgui_test_engine/imgui_te_ui.h"


ImGuiTest* AutomationShowMeImmediateApps()
{
    ImGuiTestEngine *engine = HelloImGui::GetImGuiTestEngine();

    ImGuiTest* automation = IM_REGISTER_TEST(engine, "Automation", "ShowMeImmediateApps");
    auto testFunc = [](ImGuiTestContext *ctx) {
        const char* tabImmAppsName = "//**/Demo Apps";
        const char* tabIntroName = "//**/Intro";

        ctx->MouseMove(tabImmAppsName);
        ctx->MouseClick(0);
        ctx->ItemClick("//**/demo_docking/View code");
        ctx->ItemClick("//**/demo_assets_addons/View code");
        ctx->ItemClick("//**/demo_hello_world/View code");
        ctx->MouseMove("//**/demo_hello_world/Run");
        ctx->MouseMove(tabIntroName);
        ctx->MouseClick(0);
    };
    automation->TestFunc = testFunc;
    return automation;
}
#endif // #ifdef HELLOIMGUI_WITH_TEST_ENGINE


void demo_imgui_bundle_intro()
{
#ifdef HELLOIMGUI_WITH_TEST_ENGINE
    //
    // Automations
    //

    static ImGuiTest *automationShowMeImmediateApps = nullptr;
    static bool wasAutomationInited = false;
    // Create automations upon first display
    if (HelloImGui::GetRunnerParams()->useImGuiTestEngine)
    {
        if (!wasAutomationInited)
        {
            wasAutomationInited = true;
            automationShowMeImmediateApps = AutomationShowMeImmediateApps();
        }
        // set automation speed
        ImGuiTestEngineIO& engineIo = ImGuiTestEngine_GetIO(HelloImGui::GetImGuiTestEngine());
        engineIo.ConfigRunSpeed = ImGuiTestRunSpeed_Cinematic;
        // Optional: show test engine window
        //ImGuiTestEngine_ShowTestEngineWindows(HelloImGui::GetImGuiTestEngine(), nullptr);
    }
#endif // #ifdef HELLOIMGUI_WITH_TEST_ENGINE

    ImGui::NewLine();
    ImGuiMd::RenderUnindented("*Dear ImGui Bundle: easily create ImGui applications in Python and C++. Batteries included!*");

    ImGui::NewLine();
    ImGui::NewLine();
    ImGui::NewLine();
    ImGuiMd::RenderUnindented(R"(
Welcome to the interactive manual for *Dear ImGui Bundle*! This manual present lots of examples, together with their code (in C++ and Python).

The "Demo Apps" tab is especially interesting, as it provide sample starter apps from which you can take inspiration. Click on the "View Code" button to view the apps code, and click on "Run" to run them.
)");
#ifdef HELLOIMGUI_WITH_TEST_ENGINE

    if (HelloImGui::GetRunnerParams()->useImGuiTestEngine)
    {
        if (ImGui::Button("Show me##demo_imm_apps"))
            ImGuiTestEngine_QueueTest(HelloImGui::GetImGuiTestEngine(), automationShowMeImmediateApps);
    }
#endif // #ifdef HELLOIMGUI_WITH_TEST_ENGINE


    // Navigation buttons
    {
        ImGui::Separator();
        ImGui::Dummy(HelloImGui::EmToVec2(1.f, 6.f)); // Skip 6 lines
        ImVec2 btnSize = HelloImGui::EmToVec2(0.f, 1.5f);
        if (HelloImGui::ImageButtonFromAsset("images/badge_view_sources.png", btnSize))
            ImmApp::BrowseToUrl("https://github.com/pthom/imgui_bundle");
        ImGui::SameLine();
        if (HelloImGui::ImageButtonFromAsset("images/badge_view_docs.png", btnSize))
            ImmApp::BrowseToUrl("https://pthom.github.io/imgui_bundle");
        ImGui::SameLine();
        if (HelloImGui::ImageButtonFromAsset("images/badge_interactive_manual.png", btnSize))
            ImmApp::BrowseToUrl("https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html");
    }

    AnimateLogo("images/logo_imgui_bundle_512.png", 1., ImVec2(0.5f, 3.f), 0.30f, "https://github.com/pthom/imgui_bundle");
}
