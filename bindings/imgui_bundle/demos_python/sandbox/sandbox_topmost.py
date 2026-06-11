"""
// Example demonstrating the topMost window feature
#include "hello_imgui/hello_imgui.h"
#include "imgui.h"

int main(int, char**)
{
    HelloImGui::RunnerParams runnerParams;

    runnerParams.appWindowParams.windowTitle = "TopMost Window Demo";
    runnerParams.appWindowParams.windowGeometry.size = {400, 300};

    // Enable topMost - window will stay on top of other windows
    runnerParams.appWindowParams.topMost = false;

    runnerParams.callbacks.ShowGui = []() {
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
    };

    runnerParams.platformBackendType = HelloImGui::PlatformBackendType::Sdl;
    // runnerParams.platformBackendType = HelloImGui::PlatformBackendType::Glfw;
    HelloImGui::Run(runnerParams);
    return 0;
}
"""

from imgui_bundle import hello_imgui, imgui, immapp

def show_gui():
    imgui.text("This window should stay on top of other windows!")
    imgui.separator()

    # Allow toggling topMost at runtime
    params = hello_imgui.get_runner_params().app_window_params
    top_most = params.top_most
    changed, top_most = imgui.checkbox("Keep window on top", top_most)
    if changed:
        params.top_most = top_most

    imgui.text_wrapped(
        "Note: TopMost is only supported on desktop platforms "
        "(Windows, macOS, Linux). On mobile and web platforms, "
        "this setting is ignored."
    )


def main():
    # runner_params = hello_imgui.RunnerParams()
    # runner_params.app_window_params.window_title = "TopMost Window Demo"
    # runner_params.app_window_params.window_geometry.size = (400, 300)
    # runner_params.app_window_params.top_most = False
    # runner_params.callbacks.show_gui = show_gui
    # hello_imgui.run(runner_params)

    immapp.run(show_gui, top_most=True)


if __name__ == "__main__":
    main()
