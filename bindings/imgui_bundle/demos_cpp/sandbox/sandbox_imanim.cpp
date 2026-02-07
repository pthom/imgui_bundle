#include "imgui.h"
#include "im_anim.h"
#include "immapp/runner.h"
#include "hello_imgui/hello_imgui.h"

void Gui()
{
    float dt = ImGui::GetIO().DeltaTime;
    static float target = 50.0f;
    ImGui::SliderFloat("Target", &target, 0.0f, 100.0f);

    ImGuiID id = ImGui::GetID("float_demo");
    float value = iam_tween_float(id, 0, target, 1.0f, iam_ease_preset(iam_ease_out_cubic), iam_policy_crossfade, dt);

    ImGui::ProgressBar(value / 100.0f, ImVec2(-1, 0), "");
    ImGui::SameLine();
    ImGui::Text("%.1f", value);

    ImGui::TextDisabled("iam_tween_float(id, channel, %.1f, 1.0f, ease_out_cubic, crossfade, dt)", target);
}


int main()
{
    HelloImGui::RunnerParams runner_params;
    runner_params.callbacks.ShowGui = Gui;

    ImmApp::AddOnsParams addons_params;
    addons_params.withImAnim = true;

    ImmApp::Run(runner_params, addons_params);
}