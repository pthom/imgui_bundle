###############################################################################
# This file is a part of Dear ImGui Bundle, NOT a part of ImAnim
# -----------------------------------------------------------------------------
# im_anim_demo_basics.py is a port of im_anim_demo_basics.cpp using the
# bindings provided by Dear ImGui Bundle. It is not guaranteed to be
# up-to-date with the latest version of the C++ code, but it should be
# close enough.
###############################################################################
from imgui_bundle import imgui, im_anim as iam, immapp, ImVec2, ImVec4


def IMGUI_DEMO_MARKER(section: str) -> None:
    """Marker for the interactive manual. Maps sections to source code."""
    pass


# ============================================================
# HELPER: Open/Close all collapsing headers and tree nodes
# ============================================================
_open_all = 0  # 0 = none, 1 = open all, -1 = close all


def _apply_open_all() -> None:
    global _open_all
    if _open_all != 0:
        imgui.set_next_item_open(_open_all > 0, imgui.Cond_.always)


def demo_header(label: str, demo_function) -> None:
    """Show a tree node with the demo and its source code."""
    static = demo_header
    fn_id = id(demo_function)
    if not hasattr(static, "fn_snippets"):
        static.fn_snippets = {}
    if fn_id not in static.fn_snippets:
        import inspect
        source = inspect.getsource(demo_function)
        snippet_data = immapp.snippets.SnippetData(code=source)
        snippet_data.show_copy_button = True
        snippet_data.max_height_in_lines = 30
        static.fn_snippets[fn_id] = snippet_data

    _apply_open_all()
    if imgui.tree_node_ex(label):
        if imgui.tree_node_ex("Source code"):
            snippet_data = static.fn_snippets[fn_id]
            immapp.snippets.show_code_snippet(snippet_data)
            imgui.tree_pop()
        demo_function()
        imgui.tree_pop()


# =============================================================================
# BASIC ANIMATIONS
# =============================================================================

def demo_tween_float():
    """Basic tween: smoothly animate a float value toward a target."""
    IMGUI_DEMO_MARKER("Basic Animations/Tween Float")
    imgui.text_wrapped("Smoothly animate a float toward a target. Drag the slider while animating to see crossfade blending.")
    static = demo_tween_float
    if not hasattr(static, "target"):
        static.target = 50.0

    dt = imgui.get_io().delta_time
    _, static.target = imgui.slider_float("Target", static.target, 0.0, 100.0)

    duration = 1.0
    value = iam.tween_float(
        imgui.get_id("float_demo"), # id
        0,                          # channel_id
        static.target, duration,
        iam.ease_preset(iam.ease_type.ease_out_cubic),
        iam.policy.crossfade, dt
    )
    imgui.progress_bar(value / 100.0, ImVec2(-1, 0), f"{value:.1f}")


def demo_color_tween():
    """Color tween: animate colors in perceptually uniform OKLAB space."""
    IMGUI_DEMO_MARKER("Basic Animations/Color Tween")
    imgui.text_wrapped("Animate colors in perceptually uniform OKLAB space.")
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
    duration = 0.5
    color = iam.tween_color(
        imgui.get_id("color"),  # id
        0,                      # channel_id
        colors[static.idx], duration,
        iam.ease_preset(iam.ease_type.ease_out_cubic),
        iam.policy.crossfade, iam.color_space.col_oklab, dt
    )
    imgui.same_line()
    imgui.color_button("##c", color, 0, ImVec2(100, 0))


def demo_oscillator():
    """Oscillator: continuous sine wave for pulse effects."""
    IMGUI_DEMO_MARKER("Basic Animations/Oscillator")
    imgui.text_wrapped("Continuous sine wave for pulse/glow effects. Always active, no trigger needed.")
    dt = imgui.get_io().delta_time
    amplitude = 0.3
    frequency = 1.5
    pulse = 1.0 + iam.oscillate(
        imgui.get_id("pulse"), amplitude, frequency, iam.wave_type.wave_sine, 0.0, dt
    )
    imgui.text("Pulsing:")
    imgui.same_line()
    imgui.button("Pulse!", ImVec2(80 * pulse, 30))


def demo_shake():
    """Shake: triggered decaying animation for error feedback."""
    IMGUI_DEMO_MARKER("Basic Animations/Shake")
    imgui.text_wrapped("Triggered decaying shake for error/impact feedback. Click to trigger, then it decays to zero.")
    shake_id = imgui.get_id("shake")

    if imgui.button("Trigger Shake"):
        iam.trigger_shake(shake_id)

    dt = imgui.get_io().delta_time
    intensity = 10.0
    frequency = 30.0
    decay_time = 0.5
    offset = iam.shake(shake_id, intensity, frequency, decay_time, dt)
    imgui.same_line()
    cursor = imgui.get_cursor_pos()
    imgui.set_cursor_pos(ImVec2(cursor.x + offset, cursor.y))
    imgui.text("< Shaking!")


def demo_wiggle():
    """Wiggle: continuous smooth random movement (noise-based)."""
    IMGUI_DEMO_MARKER("Basic Animations/Wiggle")
    imgui.text_wrapped("Continuous smooth random movement (noise-based). Unlike shake, it never stops. Useful for ambient/idle effects.")
    dt = imgui.get_io().delta_time
    amplitude = 8.0
    frequency = 3.0
    offset = iam.wiggle(imgui.get_id("wiggle"), amplitude, frequency, dt)
    cursor = imgui.get_cursor_pos()
    imgui.set_cursor_pos(ImVec2(cursor.x + offset, cursor.y))
    imgui.text("~ Wobbling!")


def demo_easing_showcase():
    """Easing showcase: compare different easing curves side by side."""
    IMGUI_DEMO_MARKER("Basic Animations/Easing Showcase")
    imgui.text_wrapped("Compare easing curves side by side. Each bar uses a different easing function on the same time value.")
    static = demo_easing_showcase
    if not hasattr(static, "time"):
        static.time = 0.0

    dt = imgui.get_io().delta_time
    static.time += dt
    cycle_duration = 2.0
    t = (static.time % cycle_duration) / cycle_duration  # 0..1 looping

    if imgui.button("Restart"):
        static.time = 0.0

    bar_width = imgui.get_content_region_avail().x - 100.0
    easings = [
        ("Out Cubic", iam.ease_type.ease_out_cubic),
        ("Out Bounce", iam.ease_type.ease_out_bounce),
        ("Out Elastic", iam.ease_type.ease_out_elastic),
        ("Out Back", iam.ease_type.ease_out_back),
        ("In Out Sine", iam.ease_type.ease_in_out_sine),
    ]
    for name, ease in easings:
        value = iam.eval_preset(ease, t)
        imgui.progress_bar(value, ImVec2(bar_width, 0), "")
        imgui.same_line()
        imgui.text(name)


# =============================================================================
# CLIPS (Timeline-based animations)
# =============================================================================

def demo_clip_delay():
    """Clip with delay: animation starts after a delay period."""
    IMGUI_DEMO_MARKER("Clips/Delay")
    imgui.text_wrapped("Clip with a 1-second delay before animation starts.")
    static = demo_clip_delay
    id_ch = imgui.get_id("ch")
    if not hasattr(static, "init"):
        (iam.clip.begin(imgui.get_id("delay_clip"))
            .key_float(id_ch, 0.0, 0.0, iam.ease_type.ease_out_cubic)  # time=0, value=0
            .key_float(id_ch, 1.0, 1.0)                                # time=1, value=1
            .set_delay(1.0)
            .end())
        static.init = True

    if imgui.button("Play (1s delay)"):
        iam.play(imgui.get_id("delay_clip"), imgui.get_id("delay_inst"))

    inst = iam.get_instance(imgui.get_id("delay_inst"))
    value = inst.get_float(id_ch)[1] if inst.valid() else 0.0
    imgui.progress_bar(value, ImVec2(-1, 20), "")


def demo_clip_callback():
    """Clip with callbacks: on_begin and on_complete events."""
    IMGUI_DEMO_MARKER("Clips/Callbacks")
    imgui.text_wrapped("Clip with on_begin and on_complete callbacks. Counters increment each time.")
    static = demo_clip_callback
    id_ch_scale = imgui.get_id("ch_scale")
    if not hasattr(static, "init"):
        static.begin_count = 0
        static.complete_count = 0
        (iam.clip.begin(imgui.get_id("cb_clip"))
            .key_float(id_ch_scale, 0.0, 0.5, iam.ease_type.ease_out_back)    # time=0, scale=0.5
            .key_float(id_ch_scale, 0.5, 1.2)                                 # time=0.5, scale=1.2
            .key_float(id_ch_scale, 1.0, 1.0, iam.ease_type.ease_in_out_sine) # time=1, scale=1.0
            .on_begin(lambda _: setattr(static, 'begin_count', static.begin_count + 1))
            .on_complete(lambda _: setattr(static, 'complete_count', static.complete_count + 1))
            .end())
        static.init = True

    if imgui.button("Play"):
        iam.play(imgui.get_id("cb_clip"), imgui.get_id("cb_inst"))

    inst = iam.get_instance(imgui.get_id("cb_inst"))
    scale = inst.get_float(id_ch_scale)[1] if inst.valid() else 1.0
    imgui.same_line()
    imgui.button("Animated", ImVec2(80 * scale, 30))
    imgui.text(f"on_begin: {static.begin_count}, on_complete: {static.complete_count}")


def demo_stagger():
    """Stagger: cascading animations across multiple elements."""
    IMGUI_DEMO_MARKER("Clips/Stagger")
    imgui.text_wrapped("Cascading animation: each element starts with an incremental delay.")
    static = demo_stagger
    N = 5
    id_clip = imgui.get_id("stagger_clip")
    id_ch = imgui.get_id("stagger_ch")
    if not hasattr(static, "init"):
        (iam.clip.begin(id_clip)
            .key_float(id_ch, 0.0, 0.0, iam.ease_type.ease_out_back)  # time=0, value=0
            .key_float(id_ch, 0.5, 1.0)                               # time=0.5, value=1
            .set_stagger(N, 0.15, 0.0)  # each_delay=0.15s, from_center_bias=0
            .end())
        static.init = True

    if imgui.button("Play Stagger"):
        for i in range(N):
            iam.play_stagger(id_clip, imgui.get_id(f"stag_{i}"), i)

    for i in range(N):
        inst = iam.get_instance(imgui.get_id(f"stag_{i}"))
        val = inst.get_float(id_ch)[1] if inst.valid() else 0.0
        if i > 0:
            imgui.same_line()
        imgui.button(f"{i}", ImVec2(30, 30 + 20 * val))


def demo_clip_loop():
    """Clip looping: ping-pong animation with set_loop."""
    IMGUI_DEMO_MARKER("Clips/Looping")
    imgui.text_wrapped("Ping-pong looping: the animation bounces back and forth indefinitely.")
    static = demo_clip_loop
    id_ch = imgui.get_id("loop_ch")
    if not hasattr(static, "init"):
        (iam.clip.begin(imgui.get_id("loop_clip"))
            .key_float(id_ch, 0.0, 0.0, iam.ease_type.ease_in_out_sine)  # time=0, value=0
            .key_float(id_ch, 1.0, 1.0)                                  # time=1, value=1
            .set_loop(True, iam.direction.dir_alternate)  # ping-pong
            .end())
        static.init = True

    if imgui.button("Play Loop"):
        iam.play(imgui.get_id("loop_clip"), imgui.get_id("loop_inst"))

    inst = iam.get_instance(imgui.get_id("loop_inst"))
    value = inst.get_float(id_ch)[1] if inst.valid() else 0.0
    imgui.progress_bar(value, ImVec2(-1, 20), "")


def demo_clip_chain():
    """Chaining: play clip A then clip B automatically."""
    IMGUI_DEMO_MARKER("Clips/Chaining")
    imgui.text_wrapped("Two clips chained: A scales up, then B scales back down automatically.")
    static = demo_clip_chain
    id_ch = imgui.get_id("chain_ch")
    id_clip_a = imgui.get_id("chain_a")
    id_clip_b = imgui.get_id("chain_b")
    if not hasattr(static, "init"):
        # Clip A: scale 1.0 -> 1.5 (overshoot with ease_out_back)
        (iam.clip.begin(id_clip_a)
            .key_float(id_ch, 0.0, 1.0, iam.ease_type.ease_out_back)  # time=0, scale=1.0
            .key_float(id_ch, 0.5, 1.5)                               # time=0.5, scale=1.5
            .end())
        # Clip B: scale 1.5 -> 1.0 (smooth return)
        (iam.clip.begin(id_clip_b)
            .key_float(id_ch, 0.0, 1.5, iam.ease_type.ease_in_out_sine)  # time=0, scale=1.5
            .key_float(id_ch, 0.5, 1.0)                                  # time=0.5, scale=1.0
            .end())
        static.init = True

    if imgui.button("Play A -> B"):
        iam.play(id_clip_a, imgui.get_id("chain_inst")).then(id_clip_b)

    inst = iam.get_instance(imgui.get_id("chain_inst"))
    scale = inst.get_float(id_ch)[1] if inst.valid() else 1.0
    imgui.same_line()
    imgui.button("Animated", ImVec2(80 * scale, 30))


# =============================================================================
# MAIN GUI
# =============================================================================

def im_anim_demo_basics_window(create_window: bool = False) -> None:
    global _open_all

    if create_window:
        imgui.set_next_window_size(ImVec2(650, 750), imgui.Cond_.first_use_ever)
        is_open, _ = imgui.begin("ImAnim Demo - Basics")
        if not is_open:
            imgui.end()
            return

    # Open/Close all sections
    _open_all = 0
    if imgui.button("Open All"):
        _open_all = 1
    imgui.same_line()
    if imgui.button("Close All"):
        _open_all = -1

    imgui.separator()

    _apply_open_all()
    if imgui.collapsing_header("Basic Animations"):
        demo_header("Tween Float", demo_tween_float)
        demo_header("Color Tween (OKLAB)", demo_color_tween)
        demo_header("Oscillator", demo_oscillator)
        demo_header("Shake", demo_shake)
        demo_header("Wiggle", demo_wiggle)
        demo_header("Easing Showcase", demo_easing_showcase)

    _apply_open_all()
    if imgui.collapsing_header("Clips (Timeline)"):
        demo_header("Delay", demo_clip_delay)
        demo_header("Callbacks", demo_clip_callback)
        demo_header("Stagger", demo_stagger)
        demo_header("Looping", demo_clip_loop)
        demo_header("Chaining", demo_clip_chain)

    if create_window:
        imgui.end()


if __name__ == "__main__":
    immapp.run(lambda: im_anim_demo_basics_window(False),
               with_im_anim=True, with_markdown=True,
               window_title="ImAnim Demo - Basics", window_size=(500, 700))
