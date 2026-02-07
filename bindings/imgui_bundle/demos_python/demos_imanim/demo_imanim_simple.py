"""ImAnim Simple Demo - Showcases core animation features in Python and C++.

This demo covers:
- Tweens: immediate-mode float and color animations
- Clips: timeline-based keyframe animations with delay and callbacks
- Oscillators: continuous periodic animations
- Shake: triggered feedback animations
- Paths: animation along bezier curves
"""
from imgui_bundle import imgui, im_anim as iam, immapp, ImVec2, ImVec4


def demo_tween_float():
    """Basic tween: smoothly animate a float value toward a target."""
    imgui.separator_text("Tween Float")
    static = demo_tween_float
    if not hasattr(static, "target"):
        static.target = 50.0

    dt = imgui.get_io().delta_time
    _, static.target = imgui.slider_float("Target", static.target, 0.0, 100.0)

    id = imgui.get_id("float_demo")
    value = iam.tween_float(
        id, 0, static.target, 1.0,
        iam.ease_preset(iam.ease_type.ease_out_cubic),
        iam.policy.crossfade, dt
    )

    imgui.progress_bar(value / 100.0, ImVec2(-1, 0), "")
    imgui.same_line()
    imgui.text(f"{value:.1f}")


def demo_color_tween():
    """Color tween: animate colors in perceptually uniform OKLAB space."""
    imgui.separator_text("Color Tween (OKLAB)")
    static = demo_color_tween
    if not hasattr(static, "color_idx"):
        static.color_idx = 0

    colors = [
        ImVec4(1.0, 0.3, 0.3, 1.0),  # Red
        ImVec4(0.3, 1.0, 0.3, 1.0),  # Green
        ImVec4(0.3, 0.3, 1.0, 1.0),  # Blue
        ImVec4(1.0, 1.0, 0.3, 1.0),  # Yellow
    ]

    if imgui.button("Next Color"):
        static.color_idx = (static.color_idx + 1) % len(colors)

    dt = imgui.get_io().delta_time
    target = colors[static.color_idx]
    color = iam.tween_color(
        imgui.get_id("color_demo"), 0, target, 0.5,
        iam.ease_preset(iam.ease_type.ease_out_cubic),
        iam.policy.crossfade, iam.color_space.col_oklab, dt
    )

    imgui.same_line()
    imgui.color_button("##color", color, 0, ImVec2(100, 0))
    imgui.text_disabled("OKLAB blending avoids muddy intermediate colors")


def demo_oscillator():
    """Oscillator: continuous sine wave for pulse effects."""
    imgui.separator_text("Oscillator (Pulse)")

    dt = imgui.get_io().delta_time
    # Oscillate between 0.5 and 1.5 scale
    pulse = 1.0 + iam.oscillate(
        imgui.get_id("pulse"), 0.3, 1.5,
        iam.wave_type.wave_sine, 0.0, dt
    )

    imgui.text("Pulsing button:")
    imgui.same_line()
    # Scale button size with pulse
    size = ImVec2(80 * pulse, 30)
    imgui.button("Pulse!", size)


def demo_shake():
    """Shake: triggered decaying animation for error feedback."""
    imgui.separator_text("Shake (Error Feedback)")
    static = demo_shake
    if not hasattr(static, "shake_id"):
        static.shake_id = imgui.get_id("shake_demo")

    if imgui.button("Trigger Shake"):
        iam.trigger_shake(static.shake_id)

    dt = imgui.get_io().delta_time
    offset = iam.shake(static.shake_id, 10.0, 30.0, 0.5, dt)

    imgui.same_line()
    cursor = imgui.get_cursor_pos()
    imgui.set_cursor_pos(ImVec2(cursor.x + offset, cursor.y))
    imgui.text("< Shaking text!")
    imgui.text_disabled("Use for invalid input, errors, impacts")


def demo_clip_with_callback():
    """Clip with callbacks: timeline animation with on_begin/on_complete."""
    imgui.separator_text("Clip with Callbacks")
    static = demo_clip_with_callback
    if not hasattr(static, "initialized"):
        static.initialized = False
        static.begin_count = 0
        static.complete_count = 0

    CLIP_ID = imgui.get_id("callback_clip")
    CH_SCALE = imgui.get_id("ch_scale")
    INST_ID = imgui.get_id("callback_inst")

    if not static.initialized:
        (iam.clip.begin(CLIP_ID)
            .key_float(CH_SCALE, 0.0, 0.5, iam.ease_type.ease_out_back)
            .key_float(CH_SCALE, 0.5, 1.2)
            .key_float(CH_SCALE, 1.0, 1.0, iam.ease_type.ease_in_out_sine)
            .on_begin(lambda inst_id: setattr(static, 'begin_count', static.begin_count + 1))
            .on_complete(lambda inst_id: setattr(static, 'complete_count', static.complete_count + 1))
            .end())
        static.initialized = True

    if imgui.button("Play Animation"):
        iam.play(CLIP_ID, INST_ID)

    inst = iam.get_instance(INST_ID)
    scale = 1.0
    if inst.valid():
        _, scale = inst.get_float(CH_SCALE)

    imgui.same_line()
    imgui.button("Animated", ImVec2(80 * scale, 30))
    imgui.text(f"on_begin: {static.begin_count}, on_complete: {static.complete_count}")


def demo_clip_delay():
    """Clip with delay: animation starts after a delay period."""
    imgui.separator_text("Clip with Delay")
    static = demo_clip_delay
    if not hasattr(static, "initialized"):
        static.initialized = False

    CLIP_ID = imgui.get_id("delay_clip")
    CH_VALUE = imgui.get_id("ch_value")
    INST_ID = imgui.get_id("delay_inst")

    if not static.initialized:
        (iam.clip.begin(CLIP_ID)
            .key_float(CH_VALUE, 0.0, 0.0, iam.ease_type.ease_out_cubic)
            .key_float(CH_VALUE, 1.0, 1.0)
            .set_delay(1.0)
            .end())
        static.initialized = True

    if imgui.button("Play (1s delay)"):
        iam.play(CLIP_ID, INST_ID)

    inst = iam.get_instance(INST_ID)
    value = 0.0
    if inst.valid():
        _, value = inst.get_float(CH_VALUE)

    imgui.text("Animation starts after 1 second delay:")
    imgui.progress_bar(value, ImVec2(-1, 20), "")


def demo_path():
    """Motion path: animate along a bezier curve."""
    imgui.separator_text("Motion Path")
    static = demo_path
    if not hasattr(static, "initialized"):
        static.initialized = False
        static.t = 0.0

    PATH_ID = imgui.get_id("demo_path")

    if not static.initialized:
        # Define a curved path
        (iam.path.begin(PATH_ID, ImVec2(0, 0))
            .cubic_to(ImVec2(50, -80), ImVec2(150, -80), ImVec2(200, 0))
            .cubic_to(ImVec2(250, 80), ImVec2(150, 80), ImVec2(100, 0))
            .end())
        static.initialized = True

    # Animate t from 0 to 1
    dt = imgui.get_io().delta_time
    static.t += dt * 0.3
    if static.t > 1.0:
        static.t = 0.0

    # Get position on path
    pos = iam.path_evaluate(PATH_ID, static.t)

    # Draw the path and moving point
    draw_list = imgui.get_window_draw_list()
    origin = imgui.get_cursor_screen_pos()
    origin = ImVec2(origin.x + 50, origin.y + 60)

    # Draw path curve (sample points)
    for i in range(50):
        t1 = i / 50.0
        t2 = (i + 1) / 50.0
        p1 = iam.path_evaluate(PATH_ID, t1)
        p2 = iam.path_evaluate(PATH_ID, t2)
        draw_list.add_line(
            ImVec2(origin.x + p1.x, origin.y + p1.y),
            ImVec2(origin.x + p2.x, origin.y + p2.y),
            imgui.get_color_u32(ImVec4(0.5, 0.5, 0.5, 1.0)), 2.0
        )

    # Draw moving circle
    draw_list.add_circle_filled(
        ImVec2(origin.x + pos.x, origin.y + pos.y),
        10.0, imgui.get_color_u32(ImVec4(0.3, 0.7, 1.0, 1.0))
    )

    imgui.dummy(ImVec2(300, 120))
    imgui.text(f"t = {static.t:.2f}")


def gui():
    demo_tween_float()
    demo_color_tween()
    demo_oscillator()
    demo_shake()
    demo_clip_with_callback()
    demo_clip_delay()
    demo_path()


if __name__ == "__main__":
    immapp.run(gui, with_im_anim=True, window_title="ImAnim Demo")
