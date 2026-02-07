#include "imgui.h"
#include "im_anim.h"
#include "immapp/runner.h"
#include "hello_imgui/hello_imgui.h"


void DemoTweenFloat()
{
    ImGui::SeparatorText("DemoTweenFloat");
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

void DemoClipDelay()
{
    ImGui::SeparatorText("DemoClipDelay");
    static bool delay_clip_created = false;
    auto DOC_CLIP_DELAY = ImGui::GetID("doc_clip_delay");
    auto DOC_CH_VALUE = ImGui::GetID("doc_ch_value");
    if (!delay_clip_created) {
        iam_clip::begin(DOC_CLIP_DELAY)
            .key_float(DOC_CH_VALUE, 0.0f, 0.0f, iam_ease_out_cubic)
            .key_float(DOC_CH_VALUE, 1.0f, 1.0f)
            .set_delay(1.0f)  // 1 second delay
            .end();
        delay_clip_created = true;
    }

    static ImGuiID delay_inst_id = ImGui::GetID("doc_delay_inst");

    if (ImGui::Button("Play (1s delay)##delay")) {
        iam_play(DOC_CLIP_DELAY, delay_inst_id);
    }

    iam_instance inst = iam_get_instance(delay_inst_id);
    float value = 0.0f;
    if (inst.valid()) {
        inst.get_float(DOC_CH_VALUE, &value);
    }

    ImGui::Text("Animation starts after 1 second delay:");
    ImGui::ProgressBar(value, ImVec2(-1, 20), "");
    iam_show_debug_timeline(delay_inst_id);
}

void Gui()
{
    DemoTweenFloat();
    DemoClipDelay();
}

#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main()
{
    HelloImGui::RunnerParams runner_params;
    runner_params.callbacks.ShowGui = Gui;

    ImmApp::AddOnsParams addons_params;
    addons_params.withImAnim = true;

    ImmApp::Run(runner_params, addons_params);
}
#endif
