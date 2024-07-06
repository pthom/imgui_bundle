#include "imgui.h"
#include "immapp/immapp.h"

void gui()
{
    ImGui::Text("Hello world");
    ImGui::Text("FPS = %.1f", HelloImGui::FrameRate());
}


int main()
{
    HelloImGui::RunnerParams runner_params;
    runner_params.callbacks.ShowGui = gui;
    runner_params.platformBackendType = HelloImGui::PlatformBackendType::Glfw;

    runner_params.rendererBackendOptions.openGlOptions = HelloImGui::OpenGlOptions();
    runner_params.rendererBackendOptions.openGlOptions.MajorVersion = 3;
    runner_params.rendererBackendOptions.openGlOptions.MinorVersion = 2;
    runner_params.rendererBackendOptions.openGlOptions.GlslVersion = "#version 130";
    runner_params.rendererBackendOptions.openGlOptions.UseCoreProfile = true;

    ImmApp::Run(runner_params);
}
