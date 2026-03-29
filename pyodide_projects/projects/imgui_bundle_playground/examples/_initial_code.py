import time
import numpy as np
from imgui_bundle import (implot, imgui, immapp, hello_imgui, icons_fontawesome_4,
                          imgui_knobs, imgui_md, ImVec2, __version__)


_SHOW_HEART_CODE = r'''
def show_heart():
    # Store mutable state as function attributes (avoids globals)
    state = show_heart
    if not hasattr(state, "initialized"):
        # Fill state.x and state.y whose plot is a heart
        vals = np.arange(0, np.pi * 2, 0.01)
        state.x = np.power(np.sin(vals), 3) * 16
        state.y = 13 * np.cos(vals) - 5 * np.cos(2 * vals) - 2 * np.cos(3 * vals) - np.cos(4 * vals)
        # Heart pulse rate and time tracking
        state.phase = 0.0
        state.t0 = time.time()
        state.heart_pulse_rate = 80
        state.initialized = True

    t = time.time()
    state.phase += (t - state.t0) * state.heart_pulse_rate / (np.pi * 2)
    k = 0.8 + 0.1 * np.cos(state.phase)
    state.t0 = t

    implot.begin_plot("Heart", immapp.em_to_vec2(21, 21))
    for i in range(5):
        implot.plot_line("", state.x * k, state.y * k * (1 - 0.02 * i))
    implot.end_plot()

    imgui.set_next_item_width(hello_imgui.em_size(10))
    _, state.heart_pulse_rate = imgui_knobs.knob(
        "Pulse", state.heart_pulse_rate, 30, 180,
        variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot)
'''
exec(_SHOW_HEART_CODE)


def show_info():
    import textwrap
    doc = textwrap.dedent(f"""
    Welcome to the playground!
    ===========================================
    > **Dear ImGui Bundle**, version {__version__}
    >
    > *Interactive Python & C++ apps for desktop, mobile, and web - powered by Dear ImGui.*
    >
    > Stop fighting GUI frameworks. Start building.

    Made with {icons_fontawesome_4.ICON_FA_HEART}, and running at {hello_imgui.frame_rate():.1f} FPS

    ---
    Dear ImGui Bundle includes 23 libraries. This example uses a few of them:

    | Library | Purpose |
    |---------|---------|
    | ImGui | Widgets, layouts, inputs |
    | ImPlot | 2D plots and charts. It draws the heart you see to the left |
    | imgui_knobs | Rotary knobs. It renders the knob with which you can set the heart pulse. |
    | imgui_color_text_edit | Text Editor with syntax highlighting |
    | imgui_md | Markdown! This text - including this table - is rendered via imgui_md.|

    The code block below shows the `show_heart` function, which is responsible for drawing the heart and its controls.
    *(It is also rendered using a markdown code block)*
    """)
    imgui_md.render(doc + "```python\n" + _SHOW_HEART_CODE + "\n```")


def show_post_it():
    """Draw a post-it note at the top-right corner."""
    em = hello_imgui.em_size()
    text = "Select examples from the\ndrop-down list and click Run!"
    padding = em * 0.8
    text_size = imgui.calc_text_size(text)
    note_w = text_size.x + padding * 2
    note_h = text_size.y + padding * 2

    # Position at top-right of the viewport
    viewport = imgui.get_main_viewport()
    note_x = viewport.pos.x + viewport.size.x - note_w - em * 1.5
    note_y = viewport.pos.y + em * 0.5

    dl = imgui.get_foreground_draw_list()

    # Shadow
    shadow_offset = em * 0.15
    dl.add_rect_filled(
        (note_x + shadow_offset, note_y + shadow_offset),
        (note_x + note_w + shadow_offset, note_y + note_h + shadow_offset),
        imgui.color_convert_float4_to_u32((0, 0, 0, 0.3)))

    # Yellow note
    dl.add_rect_filled(
        (note_x, note_y), (note_x + note_w, note_y + note_h),
        imgui.color_convert_float4_to_u32((1.0, 0.95, 0.55, 0.95)))

    # Folded corner triangle
    fold = em * 1.0
    dl.add_triangle_filled(
        (note_x + note_w - fold, note_y),
        (note_x + note_w, note_y),
        (note_x + note_w, note_y + fold),
        imgui.color_convert_float4_to_u32((0.85, 0.8, 0.4, 0.95)))

    # Text
    dl.add_text(
        (note_x + padding, note_y + padding),
        imgui.color_convert_float4_to_u32((0.2, 0.15, 0.0, 1.0)),
        text)


def gui():
    show_post_it()
    # Trick to create a splitter: use begin_child with ChildFlags_.resize_x
    imgui.begin_child("left", hello_imgui.em_to_vec2(22, 0), imgui.ChildFlags_.borders | imgui.ChildFlags_.resize_x)
    show_heart()
    imgui.end_child()
    imgui.same_line()
    imgui.begin_child("right")
    show_info()
    imgui.end_child()


if __name__ == "__main__":
    immapp.run(gui, window_size=(1000, 900), window_title="Hello!", with_implot=True, with_markdown=True, fps_idle=0)
