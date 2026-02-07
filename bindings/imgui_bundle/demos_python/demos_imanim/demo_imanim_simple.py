"""ImAnim Demo - Showcases animation features with simple, readable examples.

Covers: tweens, clips, oscillators, shake, paths, morphing, text along paths,
stagger, gradients, transforms, resolved tweens, and layering.
"""
from imgui_bundle import imgui, im_anim as iam, immapp, ImVec2, ImVec4
import math


# =============================================================================
# BASIC ANIMATIONS
# =============================================================================

def demo_tween_float():
    """Basic tween: smoothly animate a float value toward a target."""
    static = demo_tween_float
    if not hasattr(static, "target"):
        static.target = 50.0

    dt = imgui.get_io().delta_time
    _, static.target = imgui.slider_float("Target", static.target, 0.0, 100.0)

    value = iam.tween_float(
        imgui.get_id("float_demo"), 0, static.target, 1.0,
        iam.ease_preset(iam.ease_type.ease_out_cubic),
        iam.policy.crossfade, dt
    )
    imgui.progress_bar(value / 100.0, ImVec2(-1, 0), f"{value:.1f}")


def demo_color_tween():
    """Color tween: animate colors in perceptually uniform OKLAB space."""
    static = demo_color_tween
    if not hasattr(static, "idx"):
        static.idx = 0

    colors = [
        ImVec4(1.0, 0.3, 0.3, 1.0), ImVec4(0.3, 1.0, 0.3, 1.0),
        ImVec4(0.3, 0.3, 1.0, 1.0), ImVec4(1.0, 1.0, 0.3, 1.0),
    ]
    if imgui.button("Next Color"):
        static.idx = (static.idx + 1) % len(colors)

    dt = imgui.get_io().delta_time
    color = iam.tween_color(
        imgui.get_id("color"), 0, colors[static.idx], 0.5,
        iam.ease_preset(iam.ease_type.ease_out_cubic),
        iam.policy.crossfade, iam.color_space.col_oklab, dt
    )
    imgui.same_line()
    imgui.color_button("##c", color, 0, ImVec2(100, 0))


def demo_oscillator():
    """Oscillator: continuous sine wave for pulse effects."""
    dt = imgui.get_io().delta_time
    pulse = 1.0 + iam.oscillate(
        imgui.get_id("pulse"), 0.3, 1.5, iam.wave_type.wave_sine, 0.0, dt
    )
    imgui.text("Pulsing:")
    imgui.same_line()
    imgui.button("Pulse!", ImVec2(80 * pulse, 30))


def demo_shake():
    """Shake: triggered decaying animation for error feedback."""
    static = demo_shake
    if not hasattr(static, "id"):
        static.id = imgui.get_id("shake")

    if imgui.button("Trigger Shake"):
        iam.trigger_shake(static.id)

    dt = imgui.get_io().delta_time
    offset = iam.shake(static.id, 10.0, 30.0, 0.5, dt)
    imgui.same_line()
    cursor = imgui.get_cursor_pos()
    imgui.set_cursor_pos(ImVec2(cursor.x + offset, cursor.y))
    imgui.text("< Shaking!")


# =============================================================================
# CLIPS (Timeline-based animations)
# =============================================================================

def demo_clip_delay():
    """Clip with delay: animation starts after a delay period."""
    static = demo_clip_delay
    if not hasattr(static, "init"):
        CLIP = imgui.get_id("delay_clip")
        CH = imgui.get_id("ch")
        (iam.clip.begin(CLIP)
            .key_float(CH, 0.0, 0.0, iam.ease_type.ease_out_cubic)
            .key_float(CH, 1.0, 1.0)
            .set_delay(1.0)
            .end())
        static.init = True
        static.CLIP, static.CH = CLIP, CH

    INST = imgui.get_id("delay_inst")
    if imgui.button("Play (1s delay)"):
        iam.play(static.CLIP, INST)

    inst = iam.get_instance(INST)
    value = inst.get_float(static.CH)[1] if inst.valid() else 0.0
    imgui.progress_bar(value, ImVec2(-1, 20), "")


def demo_clip_callback():
    """Clip with callbacks: on_begin and on_complete events."""
    static = demo_clip_callback
    if not hasattr(static, "init"):
        static.begin_count = 0
        static.complete_count = 0
        CLIP = imgui.get_id("cb_clip")
        CH = imgui.get_id("ch_scale")
        (iam.clip.begin(CLIP)
            .key_float(CH, 0.0, 0.5, iam.ease_type.ease_out_back)
            .key_float(CH, 0.5, 1.2)
            .key_float(CH, 1.0, 1.0, iam.ease_type.ease_in_out_sine)
            .on_begin(lambda _: setattr(static, 'begin_count', static.begin_count + 1))
            .on_complete(lambda _: setattr(static, 'complete_count', static.complete_count + 1))
            .end())
        static.init = True
        static.CLIP, static.CH = CLIP, CH

    INST = imgui.get_id("cb_inst")
    if imgui.button("Play"):
        iam.play(static.CLIP, INST)

    inst = iam.get_instance(INST)
    scale = inst.get_float(static.CH)[1] if inst.valid() else 1.0
    imgui.same_line()
    imgui.button("Animated", ImVec2(80 * scale, 30))
    imgui.text(f"on_begin: {static.begin_count}, on_complete: {static.complete_count}")


def demo_stagger():
    """Stagger: cascading animations across multiple elements."""
    static = demo_stagger
    N = 5
    if not hasattr(static, "init"):
        CLIP = imgui.get_id("stagger_clip")
        CH = imgui.get_id("stagger_ch")
        (iam.clip.begin(CLIP)
            .key_float(CH, 0.0, 0.0, iam.ease_type.ease_out_back)
            .key_float(CH, 0.5, 1.0)
            .set_stagger(N, 0.15, 0.0)  # 0.1s delay between each
            .end())
        static.init = True
        static.CLIP, static.CH = CLIP, CH

    if imgui.button("Play Stagger"):
        for i in range(N):
            iam.play_stagger(static.CLIP, imgui.get_id(f"stag_{i}"), i)

    for i in range(N):
        inst = iam.get_instance(imgui.get_id(f"stag_{i}"))
        val = inst.get_float(static.CH)[1] if inst.valid() else 0.0
        imgui.same_line() if i > 0 else None
        imgui.button(f"{i}", ImVec2(30, 30 + 20 * val))


# =============================================================================
# PATHS
# =============================================================================

def demo_path():
    """Motion path: animate along a bezier curve."""
    static = demo_path
    if not hasattr(static, "init"):
        PATH = imgui.get_id("path")
        (iam.path.begin(PATH, ImVec2(0, 0))
            .cubic_to(ImVec2(50, -60), ImVec2(150, -60), ImVec2(200, 0))
            .cubic_to(ImVec2(250, 60), ImVec2(150, 60), ImVec2(100, 0))
            .end())
        static.init = True
        static.PATH = PATH
        static.t = 0.0

    dt = imgui.get_io().delta_time
    static.t = (static.t + dt * 0.4) % 1.0
    pos = iam.path_evaluate(static.PATH, static.t)

    dl = imgui.get_window_draw_list()
    origin = imgui.get_cursor_screen_pos()
    origin = ImVec2(origin.x + 30, origin.y + 50)

    # Draw path
    for i in range(40):
        p1 = iam.path_evaluate(static.PATH, i / 40.0)
        p2 = iam.path_evaluate(static.PATH, (i + 1) / 40.0)
        dl.add_line(ImVec2(origin.x + p1.x, origin.y + p1.y),
                    ImVec2(origin.x + p2.x, origin.y + p2.y), 0xFF888888, 2.0)
    # Draw ball
    dl.add_circle_filled(ImVec2(origin.x + pos.x, origin.y + pos.y), 8.0, 0xFFFF8844)
    imgui.dummy(ImVec2(280, 100))


def demo_path_morph():
    """Path morphing: smoothly transition between two shapes."""
    static = demo_path_morph
    if not hasattr(static, "init"):
        # Circle-ish path
        static.PATH_A = imgui.get_id("morph_a")
        (iam.path.begin(static.PATH_A, ImVec2(50, 0))
            .cubic_to(ImVec2(50, -30), ImVec2(0, -50), ImVec2(-50, 0))
            .cubic_to(ImVec2(-50, 30), ImVec2(0, 50), ImVec2(50, 0))
            .end())
        # Square-ish path
        static.PATH_B = imgui.get_id("morph_b")
        (iam.path.begin(static.PATH_B, ImVec2(40, -40))
            .line_to(ImVec2(-40, -40))
            .line_to(ImVec2(-40, 40))
            .line_to(ImVec2(40, 40))
            .close()
            .end())
        static.blend = 0.0
        static.init = True

    _, static.blend = imgui.slider_float("Blend", static.blend, 0.0, 1.0)

    dl = imgui.get_window_draw_list()
    origin = imgui.get_cursor_screen_pos()
    origin = ImVec2(origin.x + 80, origin.y + 60)

    # Draw morphed path
    for i in range(40):
        t1, t2 = i / 40.0, (i + 1) / 40.0
        p1 = iam.path_morph(static.PATH_A, static.PATH_B, t1, static.blend)
        p2 = iam.path_morph(static.PATH_A, static.PATH_B, t2, static.blend)
        dl.add_line(ImVec2(origin.x + p1.x, origin.y + p1.y),
                    ImVec2(origin.x + p2.x, origin.y + p2.y), 0xFF44AAFF, 3.0)
    imgui.dummy(ImVec2(160, 120))


def demo_text_path():
    """Text along path: render text following a curve."""
    static = demo_text_path
    if not hasattr(static, "init"):
        static.PATH = imgui.get_id("text_path")
        (iam.path.begin(static.PATH, ImVec2(0, 40))
            .quadratic_to(ImVec2(100, -20), ImVec2(200, 40))
            .end())
        iam.path_build_arc_lut(static.PATH, 64)
        static.init = True
        static.progress = 1.0

    _, static.progress = imgui.slider_float("Progress", static.progress, 0.0, 1.0)

    origin = imgui.get_cursor_screen_pos()
    opts = iam.text_path_opts()
    opts.origin = ImVec2(origin.x + 20, origin.y + 30)
    opts.color = 0xFFFFFFFF
    iam.text_path_animated(static.PATH, "Hello ImAnim!", static.progress, opts)
    imgui.dummy(ImVec2(240, 80))


# =============================================================================
# ADVANCED
# =============================================================================

def demo_gradient():
    """Gradient: animate between multi-stop color gradients."""
    static = demo_gradient
    if not hasattr(static, "init"):
        static.grad_a = iam.gradient.two_color(ImVec4(1, 0, 0, 1), ImVec4(1, 1, 0, 1))
        static.grad_b = iam.gradient.two_color(ImVec4(0, 0.5, 1, 1), ImVec4(0, 1, 0.5, 1))
        static.target_b = False
        static.init = True

    if imgui.button("Switch Gradient"):
        static.target_b = not static.target_b

    dt = imgui.get_io().delta_time
    target = static.grad_b if static.target_b else static.grad_a
    grad = iam.tween_gradient(
        imgui.get_id("grad"), 0, target, 1.0,
        iam.ease_preset(iam.ease_type.ease_in_out_cubic),
        iam.policy.crossfade, iam.color_space.col_oklab, dt
    )

    # Draw gradient bar
    dl = imgui.get_window_draw_list()
    origin = imgui.get_cursor_screen_pos()
    for i in range(100):
        t = i / 100.0
        color = grad.sample(t)
        col32 = imgui.get_color_u32(color)
        dl.add_rect_filled(ImVec2(origin.x + i * 2, origin.y),
                           ImVec2(origin.x + i * 2 + 2, origin.y + 30), col32)
    imgui.dummy(ImVec2(200, 35))


def demo_transform():
    """Transform: animate position, rotation, and scale together."""
    static = demo_transform
    if not hasattr(static, "init"):
        static.target_idx = 0
        static.init = True

    targets = [
        iam.transform(ImVec2(0, 0), 0.0, ImVec2(1, 1)),
        iam.transform(ImVec2(60, 0), math.pi / 4, ImVec2(1.5, 1.5)),
        iam.transform(ImVec2(0, 40), -math.pi / 6, ImVec2(0.8, 1.2)),
    ]

    if imgui.button("Next Transform"):
        static.target_idx = (static.target_idx + 1) % len(targets)

    dt = imgui.get_io().delta_time
    xform = iam.tween_transform(
        imgui.get_id("xform"), 0, targets[static.target_idx], 0.5,
        iam.ease_preset(iam.ease_type.ease_out_back),
        iam.policy.crossfade, iam.rotation_mode.rotation_shortest, dt
    )

    # Draw transformed rectangle
    dl = imgui.get_window_draw_list()
    origin = imgui.get_cursor_screen_pos()
    center = ImVec2(origin.x + 80 + xform.position.x, origin.y + 40 + xform.position.y)

    # Compute corners
    hw, hh = 20 * xform.scale.x, 15 * xform.scale.y
    cos_r, sin_r = math.cos(xform.rotation), math.sin(xform.rotation)
    corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    pts = [ImVec2(center.x + c[0] * cos_r - c[1] * sin_r,
                  center.y + c[0] * sin_r + c[1] * cos_r) for c in corners]
    dl.add_quad_filled(pts[0], pts[1], pts[2], pts[3], 0xFF44FF88)
    imgui.dummy(ImVec2(180, 90))


def demo_resolved():
    """Resolved tween: target computed dynamically (follows mouse)."""
    dt = imgui.get_io().delta_time
    mouse = imgui.get_mouse_pos()
    origin = imgui.get_cursor_screen_pos()

    # Resolver returns mouse position relative to origin
    def resolver():
        return ImVec2(
            max(0, min(180, mouse.x - origin.x)),
            max(0, min(60, mouse.y - origin.y))
        )

    pos = iam.tween_vec2_resolved(
        imgui.get_id("resolved"), 0, resolver, 0.3,
        iam.ease_preset(iam.ease_type.ease_out_cubic),
        iam.policy.crossfade, dt
    )

    dl = imgui.get_window_draw_list()
    dl.add_rect(origin, ImVec2(origin.x + 180, origin.y + 60), 0xFF888888)
    dl.add_circle_filled(ImVec2(origin.x + pos.x, origin.y + pos.y), 8.0, 0xFFFF4444)
    imgui.dummy(ImVec2(180, 65))
    imgui.text("(move mouse over box)")


def demo_text_stagger():
    """Text stagger: per-character animation effects."""
    static = demo_text_stagger
    if not hasattr(static, "init"):
        static.progress = 0.0
        static.effect = 0
        static.init = True

    effects = ["Fade", "Scale", "Slide Up", "Bounce", "Wave"]
    effect_map = [
        iam.text_stagger_effect.text_fx_fade,
        iam.text_stagger_effect.text_fx_scale,
        iam.text_stagger_effect.text_fx_slide_up,
        iam.text_stagger_effect.text_fx_bounce,
        iam.text_stagger_effect.text_fx_wave,
    ]

    if imgui.button("Replay"):
        static.progress = 0.0
    imgui.same_line()
    _, static.effect = imgui.combo("Effect", static.effect, effects)

    dt = imgui.get_io().delta_time
    static.progress = min(1.0, static.progress + dt * 0.5)

    opts = iam.text_stagger_opts()
    opts.pos = imgui.get_cursor_screen_pos()
    opts.effect = effect_map[static.effect]
    opts.char_delay = 0.05
    opts.char_duration = 0.3
    opts.effect_intensity = 20.0
    opts.color = 0xFFFFFFFF
    iam.text_stagger(imgui.get_id("stagger_text"), "Hello World!", static.progress, opts)
    imgui.dummy(ImVec2(150, 30))


# =============================================================================
# MAIN GUI
# =============================================================================

def gui():
    if imgui.tree_node("Basic Animations"):
        if imgui.tree_node("Tween Float"):
            demo_tween_float()
            imgui.tree_pop()
        if imgui.tree_node("Color Tween (OKLAB)"):
            demo_color_tween()
            imgui.tree_pop()
        if imgui.tree_node("Oscillator"):
            demo_oscillator()
            imgui.tree_pop()
        if imgui.tree_node("Shake"):
            demo_shake()
            imgui.tree_pop()
        imgui.tree_pop()

    if imgui.tree_node("Clips (Timeline)"):
        if imgui.tree_node("Delay"):
            demo_clip_delay()
            imgui.tree_pop()
        if imgui.tree_node("Callbacks"):
            demo_clip_callback()
            imgui.tree_pop()
        if imgui.tree_node("Stagger"):
            demo_stagger()
            imgui.tree_pop()
        imgui.tree_pop()

    if imgui.tree_node("Paths"):
        if imgui.tree_node("Motion Path"):
            demo_path()
            imgui.tree_pop()
        if imgui.tree_node("Path Morphing"):
            demo_path_morph()
            imgui.tree_pop()
        if imgui.tree_node("Text Along Path"):
            demo_text_path()
            imgui.tree_pop()
        imgui.tree_pop()

    if imgui.tree_node("Advanced"):
        if imgui.tree_node("Gradient"):
            demo_gradient()
            imgui.tree_pop()
        if imgui.tree_node("Transform"):
            demo_transform()
            imgui.tree_pop()
        if imgui.tree_node("Resolved Tween (Mouse Follow)"):
            demo_resolved()
            imgui.tree_pop()
        if imgui.tree_node("Text Stagger"):
            demo_text_stagger()
            imgui.tree_pop()
        imgui.tree_pop()


if __name__ == "__main__":
    immapp.run(gui, with_im_anim=True, window_title="ImAnim Demo", window_size=(500, 700))
