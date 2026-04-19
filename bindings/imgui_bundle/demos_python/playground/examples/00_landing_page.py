""" Dear ImGui Bundle
================================

<img src="https://traineq.org/imgui_bundle_online/projects/imgui_bundle_playground/images/logo_imgui_bundle.png" height="60">

*Interactive Python & C++ apps for desktop, mobile, and web - powered by Dear ImGui.*

Stop fighting GUI frameworks. Start building.

---

> Welcome to **Dear ImGui Bundle's Playground**, a live Python sandbox with ready-to-run demos.
>
> *Don't hesitate to edit the source code in the left panel! For example, try editing this docstring,
> then click "Run". The documentation you are reading will immediately update!*

Write Python apps that stay readable and understandable, and run with the same code on web, desktop, and mobile.

**See also:**
* [Interactive Explorer](https://traineq.org/imgui_bundle_explorer/): Interactive manual - all libraries, live demos (even more than here!), browsable source
* [Documentation](https://pthom.github.io/imgui_bundle/): Official doc - [Repository](https://github.com/pthom/imgui_bundle): Source code
* [DeepWiki](https://deepwiki.com/pthom/imgui_bundle): AI-powered Q&A about the framework
* [Discord](https://discord.gg/xkzpKMeYN3): join the community (new!)

---
### python web apps, the python way

Forget the usual labyrinth:

<img src="https://traineq.org/ImGuiBundle/i_just_want_python.jpg" height="180">

Thanks to the pyodide version of Dear ImGui Bundle, you can write apps for your browser using
almost *only python*. **No client/server, no javascript, no fuss.**


### Batteries included

Dear ImGui Bundle development started in 2022, and the number of libraries it includes
grew steadily since then. It comes with 20+ integrated libraries: plotting (ImPlot, ImPlot3D),
image debugging (ImmVision), markdown rendering, node editors, 3D gizmos, knobs, toggles,
color text editors, and more.

*The python bindings are auto-generated, so they are always up-to-date!*


"""

import math

from imgui_bundle import (
    imgui, immapp, hello_imgui, imgui_md, imgui_color_text_edit as ed, ImVec2, ImVec4, __version__,
    icons_fontawesome_4
)

# ============================================================================
# Slide code snippets (shown in the code editor, and also executed)
# ============================================================================

SLIDE_CODES = {}

SLIDE_CODES["ImPlot"] = r'''

def slide_implot(size):
    """4 diverse plot types using ImPlot subplots"""
    import numpy as np
    from imgui_bundle import implot

    s = slide_implot
    if not hasattr(s, "init"):
        np.random.seed(0)
        s.xs = np.linspace(0, 1, 501, dtype=np.float64)
        s.filled_xs = np.arange(101, dtype=np.float64)
        s.filled_ys1 = 400 + 50 * np.random.rand(101)
        s.filled_ys2 = 275 + 75 * np.random.rand(101)
        s.filled_ys3 = 150 + 75 * np.random.rand(101)
        s.shaded_xs = np.linspace(0, 1, 501, dtype=np.float64)
        s.shaded_ys = 0.25 + 0.25 * np.sin(25 * s.shaded_xs) * np.sin(5 * s.shaded_xs)
        s.shaded_hi = s.shaded_ys + 0.1 + 0.02 * np.random.rand(501)
        s.shaded_lo = s.shaded_ys - 0.1 - 0.02 * np.random.rand(501)
        s.stem_xs = np.linspace(0, 1, 51, dtype=np.float64)
        s.stem_ys = 1.0 + 0.5 * np.sin(25 * s.stem_xs) * np.cos(2 * s.stem_xs)
        s.init = True

    sub_flags = implot.SubplotFlags_.no_resize
    if implot.begin_subplots("##plots", 2, 2, size, sub_flags):
        # Animated lines
        t = imgui.get_time() * 1.5
        if implot.begin_plot("Line Plots"):
            implot.setup_axes("", "", implot.AxisFlags_.no_tick_labels, implot.AxisFlags_.no_tick_labels)
            implot.setup_axes_limits(0, 1, -0.1, 1.1)
            implot.plot_line("sin", s.xs, 0.5 + 0.5 * np.sin(6 * (s.xs + t)))
            implot.plot_line("cos", s.xs, 0.5 + 0.3 * np.cos(4 * (s.xs + t)))
            implot.end_plot()
        # Filled
        spec = implot.Spec(fill_alpha=0.25)
        if implot.begin_plot("Stock Prices"):
            implot.setup_axes("Days", "Price")
            implot.setup_axes_limits(0, 100, 0, 500)
            for name, ys in [("A", s.filled_ys1), ("B", s.filled_ys2), ("C", s.filled_ys3)]:
                implot.plot_shaded(name, s.filled_xs, ys, 0.0, spec)
                implot.plot_line(name, s.filled_xs, ys)
            implot.end_plot()
        # Shaded
        if implot.begin_plot("Shaded"):
            implot.plot_shaded("Data", s.shaded_xs, s.shaded_hi, s.shaded_lo, spec)
            implot.plot_line("Data", s.shaded_xs, s.shaded_ys, spec)
            implot.end_plot()
        # Stems
        if implot.begin_plot("Stems"):
            implot.setup_axis_limits(implot.ImAxis_.x1, 0, 1)
            implot.setup_axis_limits(implot.ImAxis_.y1, 0, 1.6)
            implot.plot_stems("Stems", s.stem_xs, s.stem_ys)
            implot.end_plot()
        implot.end_subplots()
'''

SLIDE_CODES["ImPlot3D"] = r'''
def slide_lorenz(size):
    """Lorenz attractor - butterfly effect (ImPlot3D)"""
    import numpy as np
    from imgui_bundle import implot3d

    s = slide_lorenz
    if not hasattr(s, "init"):
        s.xs, s.ys, s.zs = [0.0], [1.0], [1.05]
        s.xs2, s.ys2, s.zs2 = [0.1], [1.0], [1.05]
        s.sigma, s.rho, s.beta, s.dt = 10.0, 28.0, 8.0/3.0, 0.01
        s.init = True

    def step(xs, ys, zs):
        x, y, z = xs[-1], ys[-1], zs[-1]
        for _ in range(5):
            dx = s.sigma*(y-x); dy = x*(s.rho-z)-y; dz = x*y-s.beta*z
            x += dx*s.dt; y += dy*s.dt; z += dz*s.dt
            xs.append(x); ys.append(y); zs.append(z)
        if len(xs) > 2000:
            del xs[:len(xs)-2000]; del ys[:len(ys)-2000]; del zs[:len(zs)-2000]

    step(s.xs, s.ys, s.zs)
    step(s.xs2, s.ys2, s.zs2)

    if implot3d.begin_plot("##lorenz", size):
        implot3d.setup_axes("X", "Y", "Z",
            implot3d.AxisFlags_.auto_fit, implot3d.AxisFlags_.auto_fit, implot3d.AxisFlags_.auto_fit)
        implot3d.plot_line("Traj 1", np.array(s.xs), np.array(s.ys), np.array(s.zs))
        implot3d.plot_line("Traj 2", np.array(s.xs2), np.array(s.ys2), np.array(s.zs2))
        implot3d.end_plot()

    pos = imgui.get_item_rect_max() - hello_imgui.em_to_vec2(12, 1.2)
    imgui.set_cursor_screen_pos(pos)
    if imgui.small_button("Restart"):
        del(s.init)
'''


SLIDE_CODES["Widgets"] = r'''
def slide_widgets(size):
    """Drum sequencer with knobs, toggles, and angled headers"""
    from imgui_bundle import imgui_toggle, imgui_knobs

    s = slide_widgets

    # Init state on first run (stored as function attributes to avoid globals)
    if not hasattr(s, "init"):
        s.instruments = ["kick", "snare", "hihat", "open-hh", "tom", "clap", "rim", "crash"]
        s.n_beats = 8
        s.pattern = [[False] * len(s.instruments) for _ in range(s.n_beats)]
        s.pattern[0][0] = s.pattern[4][0] = True
        s.pattern[2][1] = s.pattern[6][1] = True
        for i in range(0, s.n_beats, 2): s.pattern[i][2] = True
        s.pattern[1][3] = s.pattern[5][3] = True
        s.pattern[3][4] = True
        s.pattern[6][5] = True
        s.playhead, s.bpm, s.playing, s.accum = 0, 140.0, True, 0.0
        s.hl_color = ImVec4(0.3, 0.5, 1.0, 0.25)
        s.volume = [i * 1.2 for i in range(len(s.instruments))]
        s.init = True

    imgui.begin_child("##widgets", size)
    em = hello_imgui.em_size()
    # Update playhead
    if s.playing:
        dt = min(imgui.get_io().delta_time, 0.1)
        s.accum += dt
        beat_interval = 60.0 / s.bpm
        if s.accum >= beat_interval:
            s.accum = 0.0  # reset instead of subtract to prevent drift
            s.playhead = (s.playhead + 1) % s.n_beats

    # Side panel width
    side_w = em * 15
    table_w = size.x - side_w - em

    # Table (left)
    n_cols = len(s.instruments) + 1
    flags = (imgui.TableFlags_.sizing_fixed_fit | imgui.TableFlags_.borders_outer
             | imgui.TableFlags_.borders_inner_h | imgui.TableFlags_.highlight_hovered_column
             | imgui.TableFlags_.scroll_x | imgui.TableFlags_.scroll_y)
    if imgui.begin_table("##seq", n_cols, flags, ImVec2(table_w, size.y - em * 2)):
        imgui.table_setup_column("Beat", imgui.TableColumnFlags_.no_hide)
        for name in s.instruments:
            imgui.table_setup_column(name,
                imgui.TableColumnFlags_.angled_header | imgui.TableColumnFlags_.width_fixed)
        imgui.table_setup_scroll_freeze(1, 2)
        imgui.table_angled_headers_row()
        imgui.table_headers_row()
        hl = imgui.color_convert_float4_to_u32(s.hl_color)
        for row in range(s.n_beats):
            imgui.push_id(row)
            imgui.table_next_row()
            is_active = row == s.playhead and s.playing
            imgui.table_set_column_index(0)
            if is_active: imgui.table_set_bg_color(imgui.TableBgTarget_.cell_bg, hl)
            imgui.text(str(row + 1))
            for col in range(len(s.instruments)):
                if imgui.table_set_column_index(col + 1):
                    if is_active: imgui.table_set_bg_color(imgui.TableBgTarget_.cell_bg, hl)
                    imgui.push_id(col)
                    _, s.pattern[row][col] = imgui.checkbox("", s.pattern[row][col])
                    imgui.pop_id()
            imgui.pop_id()

        # Volume knobs row
        imgui.table_next_row()
        imgui.table_set_column_index(0)
        for col in range(len(s.instruments)):
            if imgui.table_set_column_index(col + 1):
                _, s.volume[col] = imgui_knobs.knob(f"Vol##{col}", s.volume[col], 0, 12,
                    variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot, size=em * 2, format="%.1f")

        imgui.end_table()

    # Side panel (right)
    imgui.same_line()
    imgui.begin_group()
    imgui.text("Play")
    _, s.playing = imgui_toggle.toggle("##play", s.playing, imgui_toggle.ToggleFlags_.animated)
    imgui.spacing()
    _, s.bpm = imgui_knobs.knob("BPM", s.bpm, 60, 300,
        variant=imgui_knobs.ImGuiKnobVariant_.stepped, size=em * 4)
    imgui.spacing()

    picker_flags = (imgui.ColorEditFlags_.no_side_preview
                    | imgui.ColorEditFlags_.no_inputs
                    | imgui.ColorEditFlags_.no_label
                    | imgui.ColorEditFlags_.alpha_bar
                    | imgui.ColorEditFlags_.picker_hue_wheel)
    imgui.set_next_item_width(150)
    _, s.hl_color = imgui.color_picker4("##hl_wheel", s.hl_color, picker_flags)

    imgui.end_group()
    imgui.end_child()
'''


SLIDE_CODES["ImmVision"] = r'''
def slide_immvision(size):
    """Image inspection with synced pan/zoom (ImmVision)"""
    import numpy as np
    from imgui_bundle import immvision

    # Init images and params
    s = slide_immvision
    if not hasattr(s, "init"):
        immvision.use_rgb_color_order()
        # Generate a Mandelbrot set image
        w, h = 400, 300
        img = np.zeros((h, w, 3), dtype=np.uint8)
        for py in range(h):
            for px in range(w):
                x0 = (px - w * 0.7) / (w * 0.35)
                y0 = (py - h * 0.5) / (h * 0.45)
                x, y, it = 0.0, 0.0, 0
                while x*x + y*y <= 4 and it < 80:
                    x, y = x*x - y*y + x0, 2*x*y + y0
                    it += 1
                t = it / 80.0
                img[py, px] = [int(9*(1-t)*t*t*t*255), int(15*(1-t)*(1-t)*t*t*255), int(8.5*(1-t)*(1-t)*(1-t)*t*255)]
        s.image = img
        # Simple edge detection (no OpenCV needed)
        gray = np.mean(img, axis=2)
        dx = np.abs(np.diff(gray, axis=1, prepend=0))
        dy = np.abs(np.diff(gray, axis=0, prepend=0))
        edges = np.clip(dx + dy, 0, 255).astype(np.float64) / 255.0
        s.edges = edges
        # ImmVision params with synced zoom
        s.params1 = immvision.ImageParams()
        s.params1.image_display_size = (int(size.x * 0.3), 0)
        s.params1.zoom_key = "playground"
        s.params1.can_resize = True

        s.params2 = immvision.ImageParams()
        s.params2.image_display_size = (int(size.x * 0.3), 0)
        s.params2.zoom_key = "playground"
        s.params2.show_options_panel = True
        s.params2.can_resize = True

        s.init = True

    # Display user interface (images and help text)
    imgui.begin_child("##immvision", size)
    immvision.image("Original", s.image, s.params1)
    imgui.same_line()
    imgui.text_wrapped("\n"
        "ImmVision is an advanced image inspector / analyzer\n"
        "- Drag the images to pan\n"
        "- Use mouse wheel to zoom (both images are synced)\n"
        "- At high zoom levels, the pixels values will be displayed\n"
        "- Apply colormaps\n"
        "- Drag bottom right corner to resize images\n"
        "- etc.\n")
    immvision.image("Edges", s.edges, s.params2)
    imgui.end_child()
'''


# Execute all slide code to define the functions
for _code in SLIDE_CODES.values():
    exec(_code)

SLIDE_FUNCS = [slide_implot, slide_lorenz, slide_widgets, slide_immvision]  # type: ignore[name-defined]  # noqa: F821
SLIDE_NAMES = list(SLIDE_CODES.keys())


# ============================================================================
# Simplified carousel with arrows
# ============================================================================

_current_slide = 0
_animated_offset = 0.0
_auto_timer = 0.0
_auto_paused = False
_SLIDE_DURATION = 6.0


def _smooth_damp(current, target, speed, dt):
    return current + (target - current) * (1.0 - math.exp(-speed * dt))


def show_carousel(avail_size):
    global _current_slide, _animated_offset, _auto_timer, _auto_paused

    n = len(SLIDE_NAMES)
    em = hello_imgui.em_size()
    dt = min(imgui.get_io().delta_time, 0.1)
    if dt <= 0:
        dt = 1.0 / 60.0

    # Auto-advance
    if not _auto_paused and not imgui.is_any_item_active():
        _auto_timer += dt
        if _auto_timer > _SLIDE_DURATION:
            _current_slide = (_current_slide + 1) % n
            _auto_timer = 0.0

    # Smooth animation
    target = float(_current_slide)
    _animated_offset = _smooth_damp(_animated_offset, target, 8.0, dt)
    if abs(_animated_offset - target) < 0.001:
        _animated_offset = target

    # Layout
    nav_h = em * 2.0
    slide_h = avail_size.y - nav_h
    slide_w = avail_size.x

    # Slide area
    slide_area_pos = imgui.get_cursor_screen_pos()
    imgui.dummy(ImVec2(slide_w, slide_h))

    dl = imgui.get_window_draw_list()
    dl.push_clip_rect(slide_area_pos,
                      ImVec2(slide_area_pos.x + slide_w, slide_area_pos.y + slide_h), True)

    for i in range(n):
        sx = slide_area_pos.x + (float(i) - _animated_offset) * slide_w
        if sx > slide_area_pos.x + slide_w or sx + slide_w < slide_area_pos.x:
            continue
        imgui.set_cursor_screen_pos(ImVec2(sx, slide_area_pos.y))
        imgui.begin_child(f"##slide_{i}", ImVec2(slide_w, slide_h), False,
                          imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_background)
        content_size = ImVec2(slide_w - em * 0.5, slide_h - em * 1.5)
        imgui.text_colored(ImVec4(0.5, 0.8, 1.0, 1.0), SLIDE_NAMES[i])
        SLIDE_FUNCS[i](content_size)
        imgui.end_child()

    dl.pop_clip_rect()

    # Navigation: arrows + dots
    arrow_w = em * 2.0
    dot_r = em * 0.25
    dot_spacing = em * 1.2
    dots_w = n * dot_spacing
    total_nav_w = arrow_w * 2 + dots_w + em
    nav_x = slide_area_pos.x + (slide_w - total_nav_w) * 0.5
    nav_y = slide_area_pos.y + slide_h + em * 0.2

    # Left arrow
    imgui.set_cursor_screen_pos(ImVec2(nav_x, nav_y))
    if imgui.button(icons_fontawesome_4.ICON_FA_CHEVRON_LEFT + "##prev", ImVec2(arrow_w, em * 1.2)):
        _current_slide = (_current_slide - 1 + n) % n
        _auto_paused = True
        _auto_timer = 0.0

    # Dots
    dots_x = nav_x + arrow_w + em * 0.5
    dots_cy = nav_y + em * 0.6
    for i in range(n):
        cx = dots_x + i * dot_spacing + dot_spacing * 0.5
        imgui.set_cursor_screen_pos(ImVec2(cx - dot_r * 2, dots_cy - dot_r * 2))
        if imgui.invisible_button(f"##dot{i}", ImVec2(dot_r * 4, dot_r * 4)):
            _current_slide = i
            _auto_paused = True
            _auto_timer = 0.0
        r = dot_r * 1.3 if i == _current_slide else dot_r
        accent = imgui.get_style_color_vec4(imgui.Col_.button_hovered)
        if i == _current_slide:
            col = imgui.color_convert_float4_to_u32(accent)
        elif imgui.is_item_hovered():
            col = imgui.color_convert_float4_to_u32(ImVec4(accent.x, accent.y, accent.z, 0.6))
        else:
            col = imgui.get_color_u32(imgui.Col_.text_disabled)
        dl.add_circle_filled(ImVec2(cx, dots_cy), r, col)

    # Right arrow
    imgui.set_cursor_screen_pos(ImVec2(dots_x + dots_w + em * 0.5, nav_y))
    if imgui.button(icons_fontawesome_4.ICON_FA_CHEVRON_RIGHT + "##next", ImVec2(arrow_w, em * 1.2)):
        _current_slide = (_current_slide + 1) % n
        _auto_paused = True
        _auto_timer = 0.0


# ============================================================================
# Code editor with fade transition
# ============================================================================

_editor = None
_editor_current_slide = -1
_fade_alpha = 1.0
_fade_target_slide = -1


def show_code_editor(size):
    global _editor, _editor_current_slide, _fade_alpha, _fade_target_slide

    if _editor is None:
        _editor = ed.TextEditor()
        _editor.set_language(ed.TextEditor.Language.python())
        _editor.set_read_only_enabled(True)
        _editor.set_show_whitespaces_enabled(False)

    dt = min(imgui.get_io().delta_time, 0.1)

    # Detect slide change
    if _current_slide != _editor_current_slide and _fade_target_slide != _current_slide:
        _fade_target_slide = _current_slide

    # Fade animation
    if _fade_target_slide >= 0:
        _fade_alpha = max(0.0, _fade_alpha - dt * 4.0)
        if _fade_alpha <= 0.01:
            code = SLIDE_CODES[SLIDE_NAMES[_fade_target_slide]].strip()
            _editor.set_text(code)
            _editor_current_slide = _fade_target_slide
            _fade_target_slide = -1
    else:
        _fade_alpha = min(1.0, _fade_alpha + dt * 4.0)

    # Initial load
    if _editor_current_slide < 0:
        _editor.set_text(SLIDE_CODES[SLIDE_NAMES[0]].strip())
        _editor_current_slide = 0
        _fade_alpha = 1.0

    code_font = imgui_md.get_code_font()
    imgui.push_font(code_font.font, code_font.size)
    imgui.push_style_var(imgui.StyleVar_.alpha, _fade_alpha)
    _editor.render("##code_viewer", size, False)
    imgui.pop_style_var()
    imgui.pop_font()


# ============================================================================
# Markdown info panel
# ============================================================================



def show_info():
    imgui_md.render(__doc__)
    imgui.separator()
    imgui.text_disabled(f"Dear ImGui Bundle, version {__version__}")


# ============================================================================
# Post-it note
# ============================================================================

def show_post_it():
    em = hello_imgui.em_size()
    text = "Select examples from the\ndrop-down list and click Run!"
    padding = em * 0.4
    text_size = imgui.calc_text_size(text)
    note_w = text_size.x + padding * 2
    note_h = text_size.y + padding * 2
    viewport = imgui.get_main_viewport()
    note_x = viewport.pos.x + viewport.size.x - note_w - em * 1.5
    note_y = viewport.pos.y + em * 0.1
    dl = imgui.get_foreground_draw_list()
    shadow = em * 0.15
    dl.add_rect_filled((note_x + shadow, note_y + shadow),
        (note_x + note_w + shadow, note_y + note_h + shadow),
        imgui.color_convert_float4_to_u32((0, 0, 0, 0.3)))
    dl.add_rect_filled((note_x, note_y), (note_x + note_w, note_y + note_h),
        imgui.color_convert_float4_to_u32((1.0, 0.95, 0.55, 0.95)))
    fold = em * 1.0
    dl.add_triangle_filled((note_x + note_w - fold, note_y), (note_x + note_w, note_y),
        (note_x + note_w, note_y + fold),
        imgui.color_convert_float4_to_u32((0.85, 0.8, 0.4, 0.95)))
    dl.add_text((note_x + padding, note_y + padding),
        imgui.color_convert_float4_to_u32((0.2, 0.15, 0.0, 1.0)), text)


# ============================================================================
# Main GUI
# ============================================================================

def gui():
    show_post_it()
    avail = imgui.get_content_region_avail()

    # Left column: carousel + code editor
    left_w = avail.x * 0.5
    imgui.begin_child("left_col", ImVec2(left_w, 0),
                      imgui.ChildFlags_.borders | imgui.ChildFlags_.resize_x)
    left_avail = imgui.get_content_region_avail()

    # Carousel (top)
    carousel_h = left_avail.y * 0.6
    imgui.begin_child("carousel", ImVec2(0, carousel_h), imgui.ChildFlags_.resize_y)
    show_carousel(imgui.get_content_region_avail())
    imgui.end_child()

    # Code editor (bottom)
    imgui.begin_child("code", ImVec2(0, 0))
    show_code_editor(imgui.get_content_region_avail())
    imgui.end_child()

    imgui.end_child()

    imgui.same_line()

    # Right column: markdown info
    imgui.begin_child("right_col", ImVec2(0, 0), imgui.ChildFlags_.borders)
    show_info()
    imgui.end_child()


if __name__ == "__main__":
    immapp.run(gui, window_size=(1200, 800), window_title="Dear ImGui Bundle Playground",
               with_implot=True, with_implot3d=True, with_markdown=True, fps_idle=0, ini_disable=True)
