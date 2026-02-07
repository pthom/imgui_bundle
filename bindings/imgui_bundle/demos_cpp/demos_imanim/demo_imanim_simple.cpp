// ImAnim Simple Demo - Showcases core animation features in C++ and Python.
//
// This demo covers:
// - Tweens: immediate-mode float and color animations
// - Clips: timeline-based keyframe animations with delay and callbacks
// - Oscillators: continuous periodic animations
// - Shake: triggered feedback animations
// - Paths: animation along bezier curves

#include "imgui.h"
#include "im_anim.h"
#include "immapp/runner.h"
#include "hello_imgui/hello_imgui.h"


// Basic tween: smoothly animate a float value toward a target.
void DemoTweenFloat()
{
    ImGui::SeparatorText("Tween Float");
    static float target = 50.0f;
    float dt = ImGui::GetIO().DeltaTime;

    ImGui::SliderFloat("Target", &target, 0.0f, 100.0f);

    ImGuiID id = ImGui::GetID("float_demo");
    float value = iam_tween_float(
        id, 0, target, 1.0f,
        iam_ease_preset(iam_ease_out_cubic),
        iam_policy_crossfade, dt
    );

    ImGui::ProgressBar(value / 100.0f, ImVec2(-1, 0), "");
    ImGui::SameLine();
    ImGui::Text("%.1f", value);
}


// Color tween: animate colors in perceptually uniform OKLAB space.
void DemoColorTween()
{
    ImGui::SeparatorText("Color Tween (OKLAB)");
    static int color_idx = 0;

    ImVec4 colors[] = {
        ImVec4(1.0f, 0.3f, 0.3f, 1.0f),  // Red
        ImVec4(0.3f, 1.0f, 0.3f, 1.0f),  // Green
        ImVec4(0.3f, 0.3f, 1.0f, 1.0f),  // Blue
        ImVec4(1.0f, 1.0f, 0.3f, 1.0f),  // Yellow
    };

    if (ImGui::Button("Next Color"))
        color_idx = (color_idx + 1) % 4;

    float dt = ImGui::GetIO().DeltaTime;
    ImVec4 target = colors[color_idx];
    ImVec4 color = iam_tween_color(
        ImGui::GetID("color_demo"), 0, target, 0.5f,
        iam_ease_preset(iam_ease_out_cubic),
        iam_policy_crossfade, iam_col_oklab, dt
    );

    ImGui::SameLine();
    ImGui::ColorButton("##color", color, 0, ImVec2(100, 0));
    ImGui::TextDisabled("OKLAB blending avoids muddy intermediate colors");
}


// Oscillator: continuous sine wave for pulse effects.
void DemoOscillator()
{
    ImGui::SeparatorText("Oscillator (Pulse)");

    float dt = ImGui::GetIO().DeltaTime;
    // Oscillate between 0.7 and 1.3 scale
    float pulse = 1.0f + iam_oscillate(
        ImGui::GetID("pulse"), 0.3f, 1.5f,
        iam_wave_sine, 0.0f, dt
    );

    ImGui::Text("Pulsing button:");
    ImGui::SameLine();
    ImVec2 size(80 * pulse, 30.f);
    ImGui::Button("Pulse!", size);
}


// Shake: triggered decaying animation for error feedback.
void DemoShake()
{
    ImGui::SeparatorText("Shake (Error Feedback)");
    static ImGuiID shake_id = ImGui::GetID("shake_demo");

    if (ImGui::Button("Trigger Shake"))
        iam_trigger_shake(shake_id);

    float dt = ImGui::GetIO().DeltaTime;
    float offset = iam_shake(shake_id, 10.0f, 30.0f, 0.5f, dt);

    ImGui::SameLine();
    ImVec2 cursor = ImGui::GetCursorPos();
    ImGui::SetCursorPos(ImVec2(cursor.x + offset, cursor.y));
    ImGui::Text("< Shaking text!");
    ImGui::TextDisabled("Use for invalid input, errors, impacts");
}


// Clip with callbacks: timeline animation with on_begin/on_complete.
void DemoClipWithCallback()
{
    ImGui::SeparatorText("Clip with Callbacks");
    static bool initialized = false;
    static int begin_count = 0;
    static int complete_count = 0;

    ImGuiID CLIP_ID = ImGui::GetID("callback_clip");
    ImGuiID CH_SCALE = ImGui::GetID("ch_scale");
    ImGuiID INST_ID = ImGui::GetID("callback_inst");

    if (!initialized) {
        iam_clip::begin(CLIP_ID)
            .key_float(CH_SCALE, 0.0f, 0.5f, iam_ease_out_back)
            .key_float(CH_SCALE, 0.5f, 1.2f)
            .key_float(CH_SCALE, 1.0f, 1.0f, iam_ease_in_out_sine)
#ifdef IMGUI_BUNDLE_PYTHON_API
            .on_begin([](ImGuiID) { begin_count++; })
            .on_complete([](ImGuiID) { complete_count++; })
#else
            .on_begin([](ImGuiID, void*) { begin_count++; })
            .on_complete([](ImGuiID, void*) { complete_count++; })
#endif
            .end();
        initialized = true;
    }

    if (ImGui::Button("Play Animation"))
        iam_play(CLIP_ID, INST_ID);

    iam_instance inst = iam_get_instance(INST_ID);
    float scale = 1.0f;
    if (inst.valid())
        inst.get_float(CH_SCALE, &scale);

    ImGui::SameLine();
    ImGui::Button("Animated", ImVec2(80 * scale, 30));
    ImGui::Text("on_begin: %d, on_complete: %d", begin_count, complete_count);
}


// Clip with delay: animation starts after a delay period.
void DemoClipDelay()
{
    ImGui::SeparatorText("Clip with Delay");
    static bool initialized = false;

    ImGuiID CLIP_ID = ImGui::GetID("delay_clip");
    ImGuiID CH_VALUE = ImGui::GetID("ch_value");
    ImGuiID INST_ID = ImGui::GetID("delay_inst");

    if (!initialized) {
        iam_clip::begin(CLIP_ID)
            .key_float(CH_VALUE, 0.0f, 0.0f, iam_ease_out_cubic)
            .key_float(CH_VALUE, 1.0f, 1.0f)
            .set_delay(1.0f)
            .end();
        initialized = true;
    }

    if (ImGui::Button("Play (1s delay)"))
        iam_play(CLIP_ID, INST_ID);

    iam_instance inst = iam_get_instance(INST_ID);
    float value = 0.0f;
    if (inst.valid())
        inst.get_float(CH_VALUE, &value);

    ImGui::Text("Animation starts after 1 second delay:");
    ImGui::ProgressBar(value, ImVec2(-1, 20), "");
}


// Motion path: animate along a bezier curve.
void DemoPath()
{
    ImGui::SeparatorText("Motion Path");
    static bool initialized = false;
    static float t = 0.0f;

    ImGuiID PATH_ID = ImGui::GetID("demo_path");

    if (!initialized) {
        // Define a curved path
        iam_path::begin(PATH_ID, ImVec2(0, 0))
            .cubic_to(ImVec2(50, -80), ImVec2(150, -80), ImVec2(200, 0))
            .cubic_to(ImVec2(250, 80), ImVec2(150, 80), ImVec2(100, 0))
            .end();
        initialized = true;
    }

    // Animate t from 0 to 1
    float dt = ImGui::GetIO().DeltaTime;
    t += dt * 0.3f;
    if (t > 1.0f)
        t = 0.0f;

    // Get position on path
    ImVec2 pos = iam_path_evaluate(PATH_ID, t);

    // Draw the path and moving point
    ImDrawList* draw_list = ImGui::GetWindowDrawList();
    ImVec2 origin = ImGui::GetCursorScreenPos();
    origin.x += 50;
    origin.y += 60;

    // Draw path curve (sample points)
    for (int i = 0; i < 50; i++) {
        float t1 = i / 50.0f;
        float t2 = (i + 1) / 50.0f;
        ImVec2 p1 = iam_path_evaluate(PATH_ID, t1);
        ImVec2 p2 = iam_path_evaluate(PATH_ID, t2);
        draw_list->AddLine(
            ImVec2(origin.x + p1.x, origin.y + p1.y),
            ImVec2(origin.x + p2.x, origin.y + p2.y),
            ImGui::GetColorU32(ImVec4(0.5f, 0.5f, 0.5f, 1.0f)), 2.0f
        );
    }

    // Draw moving circle
    draw_list->AddCircleFilled(
        ImVec2(origin.x + pos.x, origin.y + pos.y),
        10.0f, ImGui::GetColorU32(ImVec4(0.3f, 0.7f, 1.0f, 1.0f))
    );

    ImGui::Dummy(ImVec2(300, 120));
    ImGui::Text("t = %.2f", t);
}


void Gui()
{
    DemoTweenFloat();
    DemoColorTween();
    DemoOscillator();
    DemoShake();
    DemoClipWithCallback();
    DemoClipDelay();
    DemoPath();
}


#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main()
{
    HelloImGui::RunnerParams runner_params;
    runner_params.callbacks.ShowGui = Gui;
    runner_params.appWindowParams.windowTitle = "ImAnim Demo";

    ImmApp::AddOnsParams addons_params;
    addons_params.withImAnim = true;

    ImmApp::Run(runner_params, addons_params);
}
#endif
