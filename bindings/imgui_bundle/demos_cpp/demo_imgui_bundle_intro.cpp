// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/hello_imgui.h"
#include "immapp/browse_to_url.h"
#include "demo_utils/animate_logo.h"

#include "imgui_test_engine/imgui_te_engine.h"
#include "imgui_test_engine/imgui_te_context.h"
#include "imgui_test_engine/imgui_te_ui.h"


ImGuiTest* AutomationShowMeCode()
{
    ImGuiTestEngine *engine = HelloImGui::GetImGuiTestEngine();

    ImGuiTest* automation = IM_REGISTER_TEST(engine, "Automation", "ShowMeCode");
    auto testOpenPopupFunc = [](ImGuiTestContext *ctx) {
        ctx->SetRef("Dear ImGui Bundle");
        ctx->ItemOpen("Code for this demo");
        ctx->Sleep(2.5);
        ctx->ItemClose("Code for this demo");

        const char* tabLoggerName = "//**/Logger";
        const char* tabIntroName = "//**/Dear ImGui Bundle";

        ctx->MouseMove(tabLoggerName);
        ctx->MouseClick(0);
        ctx->SetRef("Logger");
        ctx->ItemOpen("Code for this demo");
        ctx->ItemClose("Code for this demo");
        ctx->MouseMove(tabIntroName);
        ctx->MouseClick(0);
    };
    automation->TestFunc = testOpenPopupFunc;
    return automation;
}


ImGuiTest* AutomationShowMeImmediateApps()
{
    ImGuiTestEngine *engine = HelloImGui::GetImGuiTestEngine();

    ImGuiTest* automation = IM_REGISTER_TEST(engine, "Automation", "ShowMeImmediateApps");
    auto testOpenPopupFunc = [](ImGuiTestContext *ctx) {
        const char* tabImmAppsName = "//**/Immediate Apps";
        const char* tabIntroName = "//**/Dear ImGui Bundle";

        ctx->MouseMove(tabImmAppsName);
        ctx->MouseClick(0);
        ctx->ItemClick("//**/demo_docking/View code");
        ctx->ItemClick("//**/demo_assets_addons/View code");
        ctx->ItemClick("//**/demo_hello_world/View code");
        ctx->MouseMove("//**/demo_hello_world/Run");
        ctx->MouseMove(tabIntroName);
        ctx->MouseClick(0);
    };
    automation->TestFunc = testOpenPopupFunc;
    return automation;
}


ImGuiTest* AutomationShowMeImGuiTestEngine()
{
    ImGuiTestEngine *engine = HelloImGui::GetImGuiTestEngine();

    ImGuiTest* automation = IM_REGISTER_TEST(engine, "Automation", "ShowMeImGuiTestEngine");
    auto testOpenPopupFunc = [](ImGuiTestContext *ctx) {
        const char* tabImmAppsName = "//**/Immediate Apps";
        const char* tabIntroName = "//**/Dear ImGui Bundle";

        ctx->MouseMove(tabImmAppsName);
        ctx->MouseClick(0);
        ctx->ItemClick("//**/demo_testengine/View code");
        ctx->Sleep(2.5f);
        ctx->MouseMove("//**/demo_testengine/Run");
        ctx->MouseMove(tabIntroName);
        ctx->MouseClick(0);
    };
    automation->TestFunc = testOpenPopupFunc;
    return automation;
}


void demo_imgui_bundle_intro()
{
    //
    // Automations
    //
    static ImGuiTest *automationShowMeCode = nullptr;
    static ImGuiTest *automationShowMeImmediateApps = nullptr;
    static ImGuiTest *automationShowMeImGuiTestEngine = nullptr;
    static bool wasAutomationInited = false;
    // Create automations upon first display
    if (HelloImGui::GetRunnerParams()->useImGuiTestEngine)
    {
        if (!wasAutomationInited)
        {
            wasAutomationInited = true;
            automationShowMeCode = AutomationShowMeCode();
            automationShowMeImmediateApps = AutomationShowMeImmediateApps();
            automationShowMeImGuiTestEngine = AutomationShowMeImGuiTestEngine();
        }
        // set automation speed
        ImGuiTestEngineIO& engineIo = ImGuiTestEngine_GetIO(HelloImGui::GetImGuiTestEngine());
        engineIo.ConfigRunSpeed = ImGuiTestRunSpeed_Cinematic;
        // Optional: show test engine window
        //ImGuiTestEngine_ShowTestEngineWindows(HelloImGui::GetImGuiTestEngine(), nullptr);
    }

    ImGuiMd::RenderUnindented(R"(
        *Dear ImGui Bundle: easily create ImGui applications in Python and C++. Batteries included!*

        Welcome to the interactive manual for *Dear ImGui Bundle*! This manual present lots of examples, together with their code (in C++ and Python).

        Advices:
        * This interactive manual works best when viewed together with "Dear ImGui Bundle docs"
    )");
    ImGui::SetCursorPosX(ImGui::GetCursorPosX() + HelloImGui::EmSize(1.f));
    if (ImGui::Button("Open Dear ImGui Bundle docs"))
        ImmApp::BrowseToUrl("https://pthom.github.io/imgui_bundle/");

    ImGuiMd::RenderUnindented(R"(
        * Browse through demos in the different tabs: at the top of each tab, there is a collapsible header named "Code for this demo". Click on it to show the source code for the current demo.
    )");
    if (HelloImGui::GetRunnerParams()->useImGuiTestEngine)
    {
        ImGui::SetCursorPosX(ImGui::GetCursorPosX() + HelloImGui::EmSize(1.f));
        if (ImGui::Button("Show me##demo_code_demo"))
            ImGuiTestEngine_QueueTest(HelloImGui::GetImGuiTestEngine(), automationShowMeCode);
    }

    ImGuiMd::RenderUnindented(R"(
        * The "Immediate Apps" tab is especially interesting, as it provide sample starter apps from which you can take inspiration. Click on the "View Code" button to view the apps code, and click on "Run" to run them.
    )");
    if (HelloImGui::GetRunnerParams()->useImGuiTestEngine)
    {
        ImGui::SetCursorPosX(ImGui::GetCursorPosX() + HelloImGui::EmSize(1.f));
        if (ImGui::Button("Show me##demo_imm_apps"))
            ImGuiTestEngine_QueueTest(HelloImGui::GetImGuiTestEngine(), automationShowMeImmediateApps);
    }

    if (HelloImGui::GetRunnerParams()->useImGuiTestEngine)
    {
        ImGuiMd::RenderUnindented(R"(
            * The automations provided by the "Show me" buttons work thanks to [ImGui Test Engine](https://github.com/ocornut/imgui_test_engine), which is integrated into ImGui Bundle and available via Python and C++.
        )");
        ImGui::SetCursorPosX(ImGui::GetCursorPosX() + HelloImGui::EmSize(1.f));
        if (ImGui::Button("Show me##demo_test_engine"))
            ImGuiTestEngine_QueueTest(HelloImGui::GetImGuiTestEngine(), automationShowMeImGuiTestEngine);
        ImGuiMd::RenderUnindented("&nbsp;&nbsp;&nbsp;*Note: See [Dear ImGui Test Engine License](https://github.com/ocornut/imgui_test_engine/blob/main/imgui_test_engine/LICENSE.txt)*");
    }

    ImGuiMd::RenderUnindented(R"(
        * The best way to learn about the numerous ImGui widgets usage is to use the online "ImGui Manual" (once inside the manual, you may want to click the "Python" checkbox).
    )");
    ImGui::SetCursorPosX(ImGui::GetCursorPosX() + HelloImGui::EmSize(1.f));
    if (ImGui::Button("Open ImGui Manual"))
        ImmApp::BrowseToUrl("https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html");

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
