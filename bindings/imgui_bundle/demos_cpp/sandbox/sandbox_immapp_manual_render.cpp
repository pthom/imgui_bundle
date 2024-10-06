#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui.h"


void Gui()
{
    ImGuiMd::RenderUnindented(R"(
        # Sandbox

        Lorem ipsum dolor sit amet, consectetur adipiscing elit
    )");
    if (ImGui::Button("Save"))
    {
        // Save something
    }
    ImGui::SameLine();
    if (ImGui::Button("Load"))
    {
        // Load something
    }
}

int main(int, char **)
{

    //ImmApp::Run(runnerParams, addonsParams);

    {
        HelloImGui::RunnerParams runnerParams;
        runnerParams.callbacks.ShowGui = Gui;
        ImmApp::AddOnsParams addonsParams;
        addonsParams.withMarkdown = true;

        ImmApp::ManualRender::SetupFromRunnerParams(runnerParams, addonsParams);
        while(!HelloImGui::GetRunnerParams()->appShallExit)
            ImmApp::ManualRender::Render();
        ImmApp::ManualRender::TearDown();
    }

    {
        ImmApp::ManualRender::SetupFromGuiFunction(
            Gui,
            "Sandbox", // windowTitle
            false, // windowSizeAuto
            false, // windowRestorePreviousGeometry
            ImmApp::DefaultWindowSize, // windowSize
            10.f, // fpsIdle
            false, // withImplot
            true, // withMarkdown
            false // withNodeEditor
        );
        while(!HelloImGui::GetRunnerParams()->appShallExit)
            ImmApp::ManualRender::Render();
        ImmApp::ManualRender::TearDown();
    }

    {
        HelloImGui::SimpleRunnerParams runnerParams;
        runnerParams.guiFunction = Gui;
        ImmApp::AddOnsParams addonsParams;
        addonsParams.withMarkdown = true;
        ImmApp::ManualRender::SetupFromSimpleRunnerParams(runnerParams, addonsParams);
        while(!HelloImGui::GetRunnerParams()->appShallExit)
            ImmApp::ManualRender::Render();
        ImmApp::ManualRender::TearDown();
    }

}