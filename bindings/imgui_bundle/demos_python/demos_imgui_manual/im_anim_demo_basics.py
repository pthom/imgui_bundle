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
    IMGUI_DEMO_MARKER("Basic Animations/Color Tween")
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
    IMGUI_DEMO_MARKER("Basic Animations/Oscillator")
    dt = imgui.get_io().delta_time
    pulse = 1.0 + iam.oscillate(
        imgui.get_id("pulse"), 0.3, 1.5, iam.wave_type.wave_sine, 0.0, dt
    )
    imgui.text("Pulsing:")
    imgui.same_line()
    imgui.button("Pulse!", ImVec2(80 * pulse, 30))


def demo_shake():
    """Shake: triggered decaying animation for error feedback."""
    IMGUI_DEMO_MARKER("Basic Animations/Shake")
    shake_id = imgui.get_id("shake")

    if imgui.button("Trigger Shake"):
        iam.trigger_shake(shake_id)

    dt = imgui.get_io().delta_time
    offset = iam.shake(shake_id, 10.0, 30.0, 0.5, dt)
    imgui.same_line()
    cursor = imgui.get_cursor_pos()
    imgui.set_cursor_pos(ImVec2(cursor.x + offset, cursor.y))
    imgui.text("< Shaking!")


# =============================================================================
# CLIPS (Timeline-based animations)
# =============================================================================

def demo_clip_delay():
    """Clip with delay: animation starts after a delay period."""
    IMGUI_DEMO_MARKER("Clips/Delay")
    static = demo_clip_delay
    if not hasattr(static, "init"):
        (iam.clip.begin(imgui.get_id("delay_clip"))
            .key_float(imgui.get_id("ch"), 0.0, 0.0, iam.ease_type.ease_out_cubic)
            .key_float(imgui.get_id("ch"), 1.0, 1.0)
            .set_delay(1.0)
            .end())
        static.init = True

    if imgui.button("Play (1s delay)"):
        iam.play(imgui.get_id("delay_clip"), imgui.get_id("delay_inst"))

    inst = iam.get_instance(imgui.get_id("delay_inst"))
    value = inst.get_float(imgui.get_id("ch"))[1] if inst.valid() else 0.0
    imgui.progress_bar(value, ImVec2(-1, 20), "")


def demo_clip_callback():
    """Clip with callbacks: on_begin and on_complete events."""
    IMGUI_DEMO_MARKER("Clips/Callbacks")
    static = demo_clip_callback
    id_ch_scale = imgui.get_id("ch_scale")
    if not hasattr(static, "init"):
        static.begin_count = 0
        static.complete_count = 0
        (iam.clip.begin(imgui.get_id("cb_clip"))
            .key_float(id_ch_scale, 0.0, 0.5, iam.ease_type.ease_out_back)
            .key_float(id_ch_scale, 0.5, 1.2)
            .key_float(id_ch_scale, 1.0, 1.0, iam.ease_type.ease_in_out_sine)
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
    static = demo_stagger
    N = 5
    id_stagger_clip = imgui.get_id("stagger_clip")
    id_stagger_ch = imgui.get_id("stagger_ch")
    if not hasattr(static, "init"):
        (iam.clip.begin(id_stagger_clip)
            .key_float(id_stagger_ch, 0.0, 0.0, iam.ease_type.ease_out_back)
            .key_float(id_stagger_ch, 0.5, 1.0)
            .set_stagger(N, 0.15, 0.0)
            .end())
        static.init = True

    if imgui.button("Play Stagger"):
        for i in range(N):
            iam.play_stagger(id_stagger_clip, imgui.get_id(f"stag_{i}"), i)

    for i in range(N):
        inst = iam.get_instance(imgui.get_id(f"stag_{i}"))
        val = inst.get_float(id_stagger_ch)[1] if inst.valid() else 0.0
        if i > 0:
            imgui.same_line()
        imgui.button(f"{i}", ImVec2(30, 30 + 20 * val))


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

    _apply_open_all()
    if imgui.collapsing_header("Clips (Timeline)"):
        demo_header("Delay", demo_clip_delay)
        demo_header("Callbacks", demo_clip_callback)
        demo_header("Stagger", demo_stagger)

    if create_window:
        imgui.end()


if __name__ == "__main__":
    immapp.run(lambda: im_anim_demo_basics_window(False),
               with_im_anim=True, with_markdown=True,
               window_title="ImAnim Demo - Basics", window_size=(500, 700))
