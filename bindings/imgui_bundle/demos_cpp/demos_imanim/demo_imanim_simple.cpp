// ImAnim Simple Demo - Showcases animation features with simple, readable examples.
//
// Covers: tweens, clips, oscillators, shake, paths, morphing, text along paths,
// stagger, gradients, transforms, resolved tweens, and layering.

#include "imgui.h"
#include "im_anim.h"
#include "immapp/runner.h"
#include "hello_imgui/hello_imgui.h"
#include <cmath>
#include <string>

// Marker for the interactive manual. Maps sections to source code.
// #define IMGUI_DEMO_MARKER(section) ((void)0)

// Show a tree node with the demo (no source code display in C++).
template<typename F>
void demo_header(const char* label, F demo_function)
{
    if (ImGui::TreeNodeEx(label)) {
        demo_function();
        ImGui::TreePop();
    }
}

constexpr float PI = 3.14159265358979323846f;

// =============================================================================
// BASIC ANIMATIONS
// =============================================================================

void DemoTweenFloat()
{
    IMGUI_DEMO_MARKER("Basic Animations/Tween Float");
    static float target = 50.0f;
    float dt = ImGui::GetIO().DeltaTime;

    ImGui::SliderFloat("Target", &target, 0.0f, 100.0f);

    float value = iam_tween_float(
        ImGui::GetID("float_demo"), 0, target, 1.0f,
        iam_ease_preset(iam_ease_out_cubic),
        iam_policy_crossfade, dt
    );
    ImGui::ProgressBar(value / 100.0f, ImVec2(-1, 0), "");
    ImGui::SameLine();
    ImGui::Text("%.1f", value);
}


void DemoColorTween()
{
    IMGUI_DEMO_MARKER("Basic Animations/Color Tween");
    static int color_idx = 0;

    ImVec4 colors[] = {
        ImVec4(1.0f, 0.3f, 0.3f, 1.0f),
        ImVec4(0.3f, 1.0f, 0.3f, 1.0f),
        ImVec4(0.3f, 0.3f, 1.0f, 1.0f),
        ImVec4(1.0f, 1.0f, 0.3f, 1.0f),
    };

    if (ImGui::Button("Next Color"))
        color_idx = (color_idx + 1) % 4;

    float dt = ImGui::GetIO().DeltaTime;
    ImVec4 color = iam_tween_color(
        ImGui::GetID("color"), 0, colors[color_idx], 0.5f,
        iam_ease_preset(iam_ease_out_cubic),
        iam_policy_crossfade, iam_col_oklab, dt
    );
    ImGui::SameLine();
    ImGui::ColorButton("##c", color, 0, ImVec2(100, 0));
}


void DemoOscillator()
{
    IMGUI_DEMO_MARKER("Basic Animations/Oscillator");
    float dt = ImGui::GetIO().DeltaTime;
    float pulse = 1.0f + iam_oscillate(
        ImGui::GetID("pulse"), 0.3f, 1.5f, iam_wave_sine, 0.0f, dt
    );
    ImGui::Text("Pulsing:");
    ImGui::SameLine();
    ImGui::Button("Pulse!", ImVec2(80 * pulse, 30));
}


void DemoShake()
{
    IMGUI_DEMO_MARKER("Basic Animations/Shake");
    ImGuiID shake_id = ImGui::GetID("shake");

    if (ImGui::Button("Trigger Shake"))
        iam_trigger_shake(shake_id);

    float dt = ImGui::GetIO().DeltaTime;
    float offset = iam_shake(shake_id, 10.0f, 30.0f, 0.5f, dt);
    ImGui::SameLine();
    ImVec2 cursor = ImGui::GetCursorPos();
    ImGui::SetCursorPos(ImVec2(cursor.x + offset, cursor.y));
    ImGui::Text("< Shaking!");
}


// =============================================================================
// CLIPS (Timeline-based animations)
// =============================================================================

void DemoClipDelay()
{
    IMGUI_DEMO_MARKER("Clips/Delay");
    static bool init = false;

    if (!init) {
        iam_clip::begin(ImGui::GetID("delay_clip"))
            .key_float(ImGui::GetID("ch"), 0.0f, 0.0f, iam_ease_out_cubic)
            .key_float(ImGui::GetID("ch"), 1.0f, 1.0f)
            .set_delay(1.0f)
            .end();
        init = true;
    }

    if (ImGui::Button("Play (1s delay)"))
        iam_play(ImGui::GetID("delay_clip"), ImGui::GetID("delay_inst"));

    iam_instance inst = iam_get_instance(ImGui::GetID("delay_inst"));
    float value = 0.0f;
    if (inst.valid()) inst.get_float(ImGui::GetID("ch"), &value);
    ImGui::ProgressBar(value, ImVec2(-1, 20), "");
}


void DemoClipCallback()
{
    IMGUI_DEMO_MARKER("Clips/Callbacks");
    static bool init = false;
    static int begin_count = 0, complete_count = 0;

    auto id_ch_scale = ImGui::GetID("ch_scale");
    auto id_clip = ImGui::GetID("cb_clip");
    auto id_inst = ImGui::GetID("cb_inst");

    if (!init) {
        iam_clip::begin(ImGui::GetID("cb_clip"))
            .key_float(id_ch_scale, 0.0f, 0.5f, iam_ease_out_back)
            .key_float(id_ch_scale, 0.5f, 1.2f)
            .key_float(id_ch_scale, 1.0f, 1.0f, iam_ease_in_out_sine)
#ifdef IMGUI_BUNDLE_PYTHON_API
            .on_begin([](ImGuiID) { begin_count++; })
            .on_complete([](ImGuiID) { complete_count++; })
#else
            .on_begin([](ImGuiID, void*) { begin_count++; })
            .on_complete([](ImGuiID, void*) { complete_count++; })
#endif
            .end();
        init = true;
    }

    if (ImGui::Button("Play"))
        iam_play(id_clip, id_inst);

    iam_instance inst = iam_get_instance(id_inst);
    float scale = 1.0f;
    if (inst.valid()) inst.get_float(id_ch_scale, &scale);
    ImGui::SameLine();
    ImGui::Button("Animated", ImVec2(80 * scale, 30));
    ImGui::Text("on_begin: %d, on_complete: %d", begin_count, complete_count);
}


void DemoStagger()
{
    IMGUI_DEMO_MARKER("Clips/Stagger");
    static bool init = false;
    const int N = 5;

    if (!init) {
        iam_clip::begin(ImGui::GetID("stagger_clip"))
            .key_float(ImGui::GetID("stagger_ch"), 0.0f, 0.0f, iam_ease_out_back)
            .key_float(ImGui::GetID("stagger_ch"), 0.5f, 1.0f)
            .set_stagger(N, 0.15f, 0.0f)
            .end();
        init = true;
    }

    if (ImGui::Button("Play Stagger")) {
        for (int i = 0; i < N; i++)
            iam_play_stagger(ImGui::GetID("stagger_clip"), ImGui::GetID(std::to_string(i).c_str()), i);
    }

    for (int i = 0; i < N; i++) {
        iam_instance inst = iam_get_instance(ImGui::GetID(std::to_string(i).c_str()));
        float val = 0.0f;
        if (inst.valid()) inst.get_float(ImGui::GetID("stagger_ch"), &val);
        if (i > 0) ImGui::SameLine();
        ImGui::Button(std::to_string(i).c_str(), ImVec2(30, 30 + 20 * val));
    }
}


// =============================================================================
// PATHS
// =============================================================================

void DemoPath()
{
    IMGUI_DEMO_MARKER("Paths/Motion Path");
    static bool init = false;
    static float t = 0.0f;

    if (!init) {
        iam_path::begin(ImGui::GetID("path"), ImVec2(0, 0))
            .cubic_to(ImVec2(50, -60), ImVec2(150, -60), ImVec2(200, 0))
            .cubic_to(ImVec2(250, 60), ImVec2(150, 60), ImVec2(100, 0))
            .end();
        init = true;
    }

    float dt = ImGui::GetIO().DeltaTime;
    t = fmodf(t + dt * 0.4f, 1.0f);
    ImVec2 pos = iam_path_evaluate(ImGui::GetID("path"), t);

    ImDrawList* dl = ImGui::GetWindowDrawList();
    ImVec2 origin = ImGui::GetCursorScreenPos();
    origin.x += 30; origin.y += 50;

    for (int i = 0; i < 40; i++) {
        ImVec2 p1 = iam_path_evaluate(ImGui::GetID("path"), i / 40.0f);
        ImVec2 p2 = iam_path_evaluate(ImGui::GetID("path"), (i + 1) / 40.0f);
        dl->AddLine(ImVec2(origin.x + p1.x, origin.y + p1.y),
                    ImVec2(origin.x + p2.x, origin.y + p2.y), 0xFF888888, 2.0f);
    }
    dl->AddCircleFilled(ImVec2(origin.x + pos.x, origin.y + pos.y), 8.0f, 0xFF4488FF);
    ImGui::Dummy(ImVec2(280, 100));
}


void DemoPathMorph()
{
    IMGUI_DEMO_MARKER("Paths/Path Morphing");
    static bool init = false;
    static float blend = 0.0f;

    if (!init) {
        iam_path::begin(ImGui::GetID("morph_a"), ImVec2(50, 0))
            .cubic_to(ImVec2(50, -30), ImVec2(0, -50), ImVec2(-50, 0))
            .cubic_to(ImVec2(-50, 30), ImVec2(0, 50), ImVec2(50, 0))
            .end();
        iam_path::begin(ImGui::GetID("morph_b"), ImVec2(40, -40))
            .line_to(ImVec2(-40, -40))
            .line_to(ImVec2(-40, 40))
            .line_to(ImVec2(40, 40))
            .close()
            .end();
        init = true;
    }

    ImGui::SliderFloat("Blend", &blend, 0.0f, 1.0f);

    ImDrawList* dl = ImGui::GetWindowDrawList();
    ImVec2 origin = ImGui::GetCursorScreenPos();
    origin.x += 80; origin.y += 60;

    for (int i = 0; i < 40; i++) {
        float t1 = i / 40.0f, t2 = (i + 1) / 40.0f;
        ImVec2 p1 = iam_path_morph(ImGui::GetID("morph_a"), ImGui::GetID("morph_b"), t1, blend);
        ImVec2 p2 = iam_path_morph(ImGui::GetID("morph_a"), ImGui::GetID("morph_b"), t2, blend);
        dl->AddLine(ImVec2(origin.x + p1.x, origin.y + p1.y),
                    ImVec2(origin.x + p2.x, origin.y + p2.y), 0xFFFFAA44, 3.0f);
    }
    ImGui::Dummy(ImVec2(160, 120));
}


void DemoTextPath()
{
    IMGUI_DEMO_MARKER("Paths/Text Along Path");
    static bool init = false;
    static float progress = 1.0f;

    if (!init) {
        iam_path::begin(ImGui::GetID("text_path"), ImVec2(0, 40))
            .quadratic_to(ImVec2(100, -20), ImVec2(200, 40))
            .end();
        iam_path_build_arc_lut(ImGui::GetID("text_path"), 64);
        init = true;
    }

    ImGui::SliderFloat("Progress", &progress, 0.0f, 1.0f);

    ImVec2 origin = ImGui::GetCursorScreenPos();
    iam_text_path_opts opts;
    opts.origin = ImVec2(origin.x + 20, origin.y + 30);
    opts.color = 0xFFFFFFFF;
    iam_text_path_animated(ImGui::GetID("text_path"), "Hello ImAnim!", progress, opts);
    ImGui::Dummy(ImVec2(240, 80));
}


// =============================================================================
// ADVANCED
// =============================================================================

void DemoGradient()
{
    IMGUI_DEMO_MARKER("Advanced/Gradient");
    static bool init = false;
    static iam_gradient grad_a, grad_b;
    static bool target_b = false;

    if (!init) {
        grad_a = iam_gradient::two_color(ImVec4(1, 0, 0, 1), ImVec4(1, 1, 0, 1));
        grad_b = iam_gradient::two_color(ImVec4(0, 0.5f, 1, 1), ImVec4(0, 1, 0.5f, 1));
        init = true;
    }

    if (ImGui::Button("Switch Gradient"))
        target_b = !target_b;

    float dt = ImGui::GetIO().DeltaTime;
    iam_gradient target = target_b ? grad_b : grad_a;
    iam_gradient grad = iam_tween_gradient(
        ImGui::GetID("grad"), 0, target, 1.0f,
        iam_ease_preset(iam_ease_in_out_cubic),
        iam_policy_crossfade, iam_col_oklab, dt
    );

    ImDrawList* dl = ImGui::GetWindowDrawList();
    ImVec2 origin = ImGui::GetCursorScreenPos();
    for (int i = 0; i < 100; i++) {
        float t = i / 100.0f;
        ImVec4 color = grad.sample(t);
        ImU32 col32 = ImGui::GetColorU32(color);
        dl->AddRectFilled(ImVec2(origin.x + i * 2, origin.y),
                          ImVec2(origin.x + i * 2 + 2, origin.y + 30), col32);
    }
    ImGui::Dummy(ImVec2(200, 35));
}


void DemoTransform()
{
    IMGUI_DEMO_MARKER("Advanced/Transform");
    static int target_idx = 0;

    iam_transform targets[] = {
        iam_transform(ImVec2(0, 0), 0.0f, ImVec2(1, 1)),
        iam_transform(ImVec2(60, 0), PI / 4.f, ImVec2(1.5f, 1.5f)),
        iam_transform(ImVec2(0, 40), -PI / 6.f, ImVec2(0.8f, 1.2f)),
    };

    if (ImGui::Button("Next Transform"))
        target_idx = (target_idx + 1) % 3;

    float dt = ImGui::GetIO().DeltaTime;
    iam_transform xform = iam_tween_transform(
        ImGui::GetID("xform"), 0, targets[target_idx], 0.5f,
        iam_ease_preset(iam_ease_out_back),
        iam_policy_crossfade, iam_rotation_shortest, dt
    );

    ImDrawList* dl = ImGui::GetWindowDrawList();
    ImVec2 origin = ImGui::GetCursorScreenPos();
    ImVec2 center(origin.x + 80 + xform.position.x, origin.y + 40 + xform.position.y);

    float hw = 20 * xform.scale.x, hh = 15 * xform.scale.y;
    float cos_r = cosf(xform.rotation), sin_r = sinf(xform.rotation);
    ImVec2 pts[4];
    float corners[4][2] = {{-hw, -hh}, {hw, -hh}, {hw, hh}, {-hw, hh}};
    for (int i = 0; i < 4; i++) {
        pts[i] = ImVec2(center.x + corners[i][0] * cos_r - corners[i][1] * sin_r,
                        center.y + corners[i][0] * sin_r + corners[i][1] * cos_r);
    }
    dl->AddQuadFilled(pts[0], pts[1], pts[2], pts[3], 0xFF88FF44);
    ImGui::Dummy(ImVec2(180, 90));
}


void DemoResolved()
{
    IMGUI_DEMO_MARKER("Advanced/Resolved Tween");
    float dt = ImGui::GetIO().DeltaTime;
    ImVec2 mouse = ImGui::GetMousePos();
    ImVec2 origin = ImGui::GetCursorScreenPos();

    // Capture for resolver
    static ImVec2 s_mouse, s_origin;
    s_mouse = mouse; s_origin = origin;

#ifdef IMGUI_BUNDLE_PYTHON_API
    auto resolver = []() -> ImVec2 {
        return ImVec2(
            fmaxf(0, fminf(180, s_mouse.x - s_origin.x)),
            fmaxf(0, fminf(60, s_mouse.y - s_origin.y))
        );
    };
    ImVec2 pos = iam_tween_vec2_resolved(
        ImGui::GetID("resolved"), 0, resolver, 0.3f,
        iam_ease_preset(iam_ease_out_cubic),
        iam_policy_crossfade, dt
    );
#else
    auto resolver = [](void*) -> ImVec2 {
        return ImVec2(
            fmaxf(0, fminf(180, s_mouse.x - s_origin.x)),
            fmaxf(0, fminf(60, s_mouse.y - s_origin.y))
        );
    };
    ImVec2 pos = iam_tween_vec2_resolved(
        ImGui::GetID("resolved"), 0, resolver, nullptr, 0.3f,
        iam_ease_preset(iam_ease_out_cubic),
        iam_policy_crossfade, dt
    );
#endif

    ImDrawList* dl = ImGui::GetWindowDrawList();
    dl->AddRect(origin, ImVec2(origin.x + 180, origin.y + 60), 0xFF888888);
    dl->AddCircleFilled(ImVec2(origin.x + pos.x, origin.y + pos.y), 8.0f, 0xFF4444FF);
    ImGui::Dummy(ImVec2(180, 65));
    ImGui::Text("(move mouse over box)");
}


void DemoTextStagger()
{
    IMGUI_DEMO_MARKER("Advanced/Text Stagger");
    static float progress = 0.0f;
    static int effect = 0;

    const char* effects[] = {"Fade", "Scale", "Slide Up", "Bounce", "Wave"};
    int effect_map[] = {iam_text_fx_fade, iam_text_fx_scale, iam_text_fx_slide_up,
                        iam_text_fx_bounce, iam_text_fx_wave};

    if (ImGui::Button("Replay"))
        progress = 0.0f;
    ImGui::SameLine();
    ImGui::Combo("Effect", &effect, effects, 5);

    float dt = ImGui::GetIO().DeltaTime;
    progress = fminf(1.0f, progress + dt * 0.5f);

    iam_text_stagger_opts opts;
    opts.pos = ImGui::GetCursorScreenPos();
    opts.effect = effect_map[effect];
    opts.char_delay = 0.05f;
    opts.char_duration = 0.3f;
    opts.effect_intensity = 20.0f;
    opts.color = 0xFFFFFFFF;
    iam_text_stagger(ImGui::GetID("stagger_text"), "Hello World!", progress, opts);
    ImGui::Dummy(ImVec2(150, 30));
}


// =============================================================================
// MAIN GUI
// =============================================================================

void Gui()
{
    if (ImGui::TreeNode("Basic Animations")) {
        demo_header("Tween Float", DemoTweenFloat);
        demo_header("Color Tween (OKLAB)", DemoColorTween);
        demo_header("Oscillator", DemoOscillator);
        demo_header("Shake", DemoShake);
        ImGui::TreePop();
    }

    if (ImGui::TreeNode("Clips (Timeline)")) {
        demo_header("Delay", DemoClipDelay);
        demo_header("Callbacks", DemoClipCallback);
        demo_header("Stagger", DemoStagger);
        ImGui::TreePop();
    }

    if (ImGui::TreeNode("Paths")) {
        demo_header("Motion Path", DemoPath);
        demo_header("Path Morphing", DemoPathMorph);
        demo_header("Text Along Path", DemoTextPath);
        ImGui::TreePop();
    }

    if (ImGui::TreeNode("Advanced")) {
        demo_header("Gradient", DemoGradient);
        demo_header("Transform", DemoTransform);
        demo_header("Resolved Tween (Mouse Follow)", DemoResolved);
        demo_header("Text Stagger", DemoTextStagger);
        ImGui::TreePop();
    }
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
