// Example demonstrating the topMost window feature
#include "hello_imgui/hello_imgui.h"
#include "imgui.h"

void ShowGui()
{
    ImGui::Text("This window should stay on top of other windows!");
    ImGui::Separator();

    // Allow toggling topMost at runtime
    auto& params = HelloImGui::GetRunnerParams()->appWindowParams;
    bool topMost = params.topMost;
    if (ImGui::Checkbox("Keep window on top", &topMost)) {
        params.topMost = topMost;
    }

    ImGui::TextWrapped(
        "Note: TopMost is only supported on desktop platforms "
        "(Windows, macOS, Linux). On mobile and web platforms, "
        "this setting is ignored."
    );
}

int main(int, char**)
{
    // HelloImGui::RunnerParams runnerParams;
    // runnerParams.appWindowParams.windowTitle = "TopMost Window Demo";
    // runnerParams.appWindowParams.windowGeometry.size = {400, 300};
    // runnerParams.appWindowParams.topMost = false;
    // runnerParams.callbacks.ShowGui = ShowGui;
    // //runnerParams.platformBackendType = HelloImGui::PlatformBackendType::Sdl;
    // runnerParams.platformBackendType = HelloImGui::PlatformBackendType::Glfw;
    // HelloImGui::Run(runnerParams);

    HelloImGui::Run(HelloImGui::SimpleRunnerParams {
        .guiFunction = ShowGui,
        .windowTitle = "TopMost Window Demo",
        .topMost = true
    });

    return 0;
}

