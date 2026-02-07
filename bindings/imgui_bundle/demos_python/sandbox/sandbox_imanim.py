from imgui_bundle import imgui, im_anim as iam, immapp, ImVec2

target = 50.0

def gui():
    global target
    dt = imgui.get_io().delta_time
    _, target = imgui.slider_float("Target", target, 0.0, 100.0)

    id = imgui.get_id("float_demo")
    value = iam.tween_float(id, 0, target, 1.0, iam.ease_preset(iam.ease_type.ease_out_cubic), iam.policy.crossfade, dt)

    imgui.progress_bar(value / 100.0, ImVec2(-1, 0), "")
    imgui.same_line()
    imgui.text(f"{value:.1f}")

    imgui.text_disabled(f"iam.tween_float(id, channel, {target:.1f}, 1.0, ease_out_cubic, crossfade, dt)")


if __name__ == "__main__":
    immapp.run(gui, with_im_anim=True)


"""
    static float target = 50.0f;
    ImGui::SliderFloat("Target", &target, 0.0f, 100.0f);

    ImGuiID id = ImHashStr("float_demo");
    float value = iam_tween_float(id, 0, target, 1.0f, iam_ease_preset(iam_ease_out_cubic), iam_policy_crossfade, dt);

    ImGui::ProgressBar(value / 100.0f, ImVec2(-1, 0), "");
    ImGui::SameLine();
    ImGui::Text("%.1f", value);

    ImGui::TextDisabled("iam_tween_float(id, channel, %.1f, 1.0f, ease_out_cubic, crossfade, dt)", target);
"""