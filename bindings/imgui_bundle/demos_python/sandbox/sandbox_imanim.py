from imgui_bundle import imgui, im_anim as iam, immapp, ImVec2


def demo_tween_float():
    imgui.separator_text("DemoTweenFloat")
    static = demo_tween_float
    if not hasattr(static, "target"):
        static.target = 50.0

    dt = imgui.get_io().delta_time
    _, static.target = imgui.slider_float("Target", static.target, 0.0, 100.0)

    id = imgui.get_id("float_demo")
    value = iam.tween_float(id, 0, static.target, 1.0, iam.ease_preset(iam.ease_type.ease_out_cubic), iam.policy.crossfade, dt)

    imgui.progress_bar(value / 100.0, ImVec2(-1, 0), "")
    imgui.same_line()
    imgui.text(f"{value:.1f}")

    imgui.text_disabled(f"iam.tween_float(id, channel, {static.target:.1f}, 1.0, ease_out_cubic, crossfade, dt)")


def demo_clip_delay():
    imgui.separator_text("DemoClipDelay")
    static = demo_clip_delay
    if not hasattr(static, "delay_clip_created"):
        static.delay_clip_created = False

    DOC_CLIP_DELAY = imgui.get_id("doc_clip_delay")
    DOC_CH_VALUE = imgui.get_id("doc_ch_value")

    if not static.delay_clip_created:
        (iam.clip.begin(DOC_CLIP_DELAY)
        .key_float(DOC_CH_VALUE, 0.0, 0.0, iam.ease_type.ease_out_cubic)
        .key_float(DOC_CH_VALUE, 1.0, 1.0)
        .set_delay(1.0)  # 1 second delay
        .end())
        static.delay_clip_created = True

    if imgui.button("Play (1s delay)##delay"):
        iam.play(DOC_CLIP_DELAY, imgui.get_id("doc_delay_inst"))

    inst = iam.get_instance(imgui.get_id("doc_delay_inst"))
    value = 0.0
    if inst.valid():
        _, value = inst.get_float(DOC_CH_VALUE)
    imgui.text("Animation starts after 1 second delay:")
    imgui.progress_bar(value, ImVec2(-1, 20), "")
    iam.show_debug_timeline(imgui.get_id("doc_delay_inst"))


def gui():
    demo_tween_float()
    demo_clip_delay()


if __name__ == "__main__":
    immapp.run(gui, with_im_anim=True)


"""
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
"""