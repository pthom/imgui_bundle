#include "immapp/immapp.h"
#include "imgui.h"
#include "hello_imgui/hello_imgui.h"
#include "imspinner/imspinner.h"
#include "imgui_md_wrapper.h"

int main(int, char **)
{
    auto gui = [&]()
    {
        ImGui::Text("Current FPS: %.1f", HelloImGui::FrameRate());
        ImGui::TextWrapped(R"(

In order to reduce the CPU usage, the FPS is reduced automatically when no user interaction is detected.

As a consequence, the animation may below not be fluid. However, if you move the mouse over this window,
the FPS will rise and the animation will be smooth again.
        )");

        auto color = ImVec4(0.3, 0.5, 0.9, 1.0);
        float radius1 = ImGui::GetFontSize();
        ImSpinner::SpinnerAngTriple("spinner_arc_fade", radius1, radius1 * 1.5, radius1 * 2., 2.5, color, color, color);

        ImGui::TextWrapped("You can adjust HelloImGui::GetRunnerParams()->fpdIdling.fpsIdle if you need smoother animations when the app is idle. "
                           "A value of 0 means that the refresh will be as fast as possible");

        ImGui::NewLine();
        auto runnerParams = HelloImGui::GetRunnerParams();
        ImGui::SliderFloat("runner_params.fpsIdle", &(runnerParams->fpsIdling.fpsIdle), 0.f, 60.f);

        ImGui::Text("You can also set HelloImGui::GetRunnerParams()->fpdIdling.enableIdling.");
        ImGui::Checkbox("Enable Idling", &runnerParams->fpsIdling.enableIdling);
    };

    ImmApp::Run(
        HelloImGui::SimpleRunnerParams{
            .guiFunction=gui,
            .windowTitle="demo_powersave",
            .windowSize={640, 400},
            .fpsIdle = 3.f
        },
        ImmApp::AddOnsParams{
        }
    );
    return 0;
}
