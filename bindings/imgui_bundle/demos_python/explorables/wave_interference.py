"""Wave Interference
==================

Two point sources emit circular waves that combine to create
interference patterns. Bright regions: constructive (waves add up).
Dark regions: destructive (waves cancel out).

Drag the sources to move them. Adjust frequency and amplitude
to explore different patterns.
"""

import numpy as np
from imgui_bundle import imgui, implot, immapp, hello_imgui, imgui_md, imgui_knobs, imgui_toggle, icons_fontawesome_4
from imgui_bundle import ImVec2, ImVec4
import time


# =============================================================================
# Wave computation
# =============================================================================

def compute_wave_field(sources, t, grid_x, grid_y, wavelength, decay):
    """Compute the combined wave field from multiple point sources.
    Returns a 2D array of wave amplitudes."""
    field = np.zeros_like(grid_x)
    for sx, sy, amp, phase in sources:
        dx = grid_x - sx
        dy = grid_y - sy
        r = np.sqrt(dx**2 + dy**2) + 1e-6
        k = 2 * np.pi / wavelength
        # Wave with radial decay
        envelope = amp / (1 + decay * r)
        field += envelope * np.sin(k * r - 2 * np.pi * t + phase)
    return field


# =============================================================================
# Colormap: convert wave amplitude to RGB
# =============================================================================

def amplitude_to_color_buffer(field, vmin, vmax):
    """Convert a 2D amplitude field to an RGBA uint8 buffer for display.
    Uses a blue-white-red diverging colormap centered at 0."""
    norm = np.clip((field - vmin) / (vmax - vmin + 1e-10), 0, 1)
    # Diverging colormap: blue -> dark -> red
    r = np.clip(2 * norm - 1, 0, 1)
    b = np.clip(1 - 2 * norm, 0, 1)
    # Intensity (bright at extremes, dark at center)
    intensity = np.abs(2 * norm - 1)
    g = intensity * 0.3
    r = (r * 0.7 + intensity * 0.3)
    b = (b * 0.7 + intensity * 0.3)

    rgba = np.zeros((*field.shape, 4), dtype=np.uint8)
    rgba[:, :, 0] = (r * 255).astype(np.uint8)
    rgba[:, :, 1] = (g * 255).astype(np.uint8)
    rgba[:, :, 2] = (b * 255).astype(np.uint8)
    rgba[:, :, 3] = 255
    return rgba


# =============================================================================
# Application state
# =============================================================================

class Source:
    def __init__(self, x: float, y: float, amp: float = 1.0, phase: float = 0.0):
        self.x = x
        self.y = y
        self.amp = amp
        self.phase = phase


class AppState:
    def __init__(self):
        self.sources = [
            Source(-3.0, 0.0, 1.0, 0.0),
            Source(3.0, 0.0, 1.0, 0.0),
        ]
        self.wavelength = 2.0
        self.frequency = 1.0
        self.decay = 0.1
        self.resolution = 200
        self.field_size = 15.0

        self.paused = False
        self.show_sources = True
        self.show_cross_section = True
        self.speed = 1.0

        self.t = 0.0
        self.last_time = time.time()

        # Precompute grid
        self._update_grid()

        # Dragging
        self.dragging_source = -1

    def _update_grid(self):
        s = self.field_size
        lin = np.linspace(-s, s, self.resolution)
        self.grid_x, self.grid_y = np.meshgrid(lin, lin)
        self.lin = lin

    def update(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        if not self.paused:
            self.t += dt * self.frequency * self.speed

    def get_field(self):
        src_data = [(s.x, s.y, s.amp, s.phase) for s in self.sources]
        return compute_wave_field(src_data, self.t, self.grid_x, self.grid_y,
                                 self.wavelength, self.decay)


# =============================================================================
# Drawing the wave field
# =============================================================================

def draw_wave_field(state: AppState, origin: ImVec2, size: ImVec2):
    """Draw the wave interference pattern using DrawList rectangles."""
    draw_list = imgui.get_window_draw_list()
    field = state.get_field()
    max_amp = max(np.max(np.abs(field)), 0.01)

    res = state.resolution
    cell_w = size.x / res
    cell_h = size.y / res

    # Downsample for performance if needed
    step = max(1, res // 150)
    for iy in range(0, res, step):
        for ix in range(0, res, step):
            v = field[iy, ix] / max_amp  # -1 to 1

            # Blue-black-red colormap
            if v > 0:
                r, g, b = 0.3 + 0.7 * v, 0.1 * v, 0.1
            else:
                av = -v
                r, g, b = 0.1, 0.1 * av, 0.3 + 0.7 * av

            col = imgui.get_color_u32(ImVec4(r, g, b, 1.0))
            px = origin.x + ix * cell_w
            py = origin.y + iy * cell_h
            draw_list.add_rect_filled(
                ImVec2(px, py),
                ImVec2(px + cell_w * step + 1, py + cell_h * step + 1),
                col)

    # Draw source positions
    if state.show_sources:
        s = state.field_size
        for i, src in enumerate(state.sources):
            sx = origin.x + (src.x + s) / (2 * s) * size.x
            sy = origin.y + (src.y + s) / (2 * s) * size.y
            # Pulsing ring
            pulse = 0.5 + 0.5 * np.sin(state.t * 2 * np.pi * 3)
            draw_list.add_circle(
                ImVec2(sx, sy), 12 + 4 * pulse,
                imgui.get_color_u32(ImVec4(1, 1, 1, 0.7)), 0, 2.0)
            draw_list.add_circle_filled(
                ImVec2(sx, sy), 6,
                imgui.get_color_u32(ImVec4(1, 1, 0.2, 1.0)))
            # Label
            draw_list.add_text(ImVec2(sx + 10, sy - 8),
                             imgui.get_color_u32(ImVec4(1, 1, 1, 0.8)),
                             f"S{i+1}")

    return field


def handle_source_dragging(state: AppState, origin: ImVec2, size: ImVec2):
    """Allow dragging sources with the mouse."""
    mouse = imgui.get_mouse_pos()
    s = state.field_size

    if imgui.is_mouse_clicked(0):
        for i, src in enumerate(state.sources):
            sx = origin.x + (src.x + s) / (2 * s) * size.x
            sy = origin.y + (src.y + s) / (2 * s) * size.y
            dist = np.sqrt((mouse.x - sx)**2 + (mouse.y - sy)**2)
            if dist < 20:
                state.dragging_source = i
                break

    if imgui.is_mouse_released(0):
        state.dragging_source = -1

    if state.dragging_source >= 0 and imgui.is_mouse_dragging(0):
        src = state.sources[state.dragging_source]
        src.x = (mouse.x - origin.x) / size.x * 2 * s - s
        src.y = (mouse.y - origin.y) / size.y * 2 * s - s
        src.x = np.clip(src.x, -s * 0.9, s * 0.9)
        src.y = np.clip(src.y, -s * 0.9, s * 0.9)


# =============================================================================
# GUI
# =============================================================================

FA_PLAY = icons_fontawesome_4.ICON_FA_PLAY
FA_PAUSE = icons_fontawesome_4.ICON_FA_PAUSE
FA_PLUS = icons_fontawesome_4.ICON_FA_PLUS
FA_MINUS = icons_fontawesome_4.ICON_FA_MINUS


def gui(state: AppState):
    state.update()
    em = hello_imgui.em_size()

    # Controls (left column)
    imgui.begin_child("controls", ImVec2(em * 20, 0))

    imgui_md.render(__doc__)
    imgui.spacing()

    # Wavelength, Speed and Decay knobs
    _, state.wavelength = imgui_knobs.knob(
        "Wave", state.wavelength, 0.5, 8.0,
        speed=0.02, variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot,
        format="%.1f")
    imgui.same_line()
    _, state.speed = imgui_knobs.knob(
        "Speed", state.speed, 0.1, 3.0,
        speed=0.01, variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot,
        format="%.1fx")
    imgui.same_line()
    _, state.decay = imgui_knobs.knob(
        "Decay", state.decay, 0.0, 0.5,
        speed=0.005, variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot,
        format="%.2f")

    imgui.spacing()

    # Source management
    imgui.text("Sources")
    for i, src in enumerate(state.sources):
        imgui.push_id(i)
        imgui.text(f"S{i+1}:")
        imgui.same_line()
        imgui.set_next_item_width(em * 4)
        _, src.amp = imgui.slider_float("Amp##", src.amp, 0.1, 3.0, "%.1f")
        imgui.same_line()
        imgui.set_next_item_width(em * 4)
        _, src.phase = imgui.slider_float("Phase##", src.phase, 0.0, 2 * np.pi, "%.1f")
        imgui.pop_id()

    imgui.spacing()
    rounding = em * 0.5
    imgui.push_style_var(imgui.StyleVar_.frame_rounding, rounding)
    small_btn = ImVec2(em * 2.0, em * 1.8)
    if imgui.button(FA_PLUS, small_btn) and len(state.sources) < 6:
        state.sources.append(Source(
            np.random.uniform(-5, 5),
            np.random.uniform(-5, 5)))
    imgui.same_line()
    if imgui.button(FA_MINUS, small_btn) and len(state.sources) > 1:
        state.sources.pop()
    imgui.same_line()
    imgui.text("Add/Remove")
    imgui.pop_style_var()

    imgui.spacing()

    # Display options
    _, state.show_sources = imgui_toggle.toggle("Sources##tog", state.show_sources)
    imgui.same_line()
    imgui.text("Show sources")

    _, state.show_cross_section = imgui_toggle.toggle("Cross##tog", state.show_cross_section)
    imgui.same_line()
    imgui.text("Cross-section")

    # Cross-section plot
    if state.show_cross_section:
        imgui.spacing()
        imgui.separator()
        imgui.spacing()
        imgui.text("Horizontal cross-section (y=0)")
        field = state.get_field()
        mid_row = state.resolution // 2
        cross = field[mid_row, :]
        xs = state.lin
        if implot.begin_plot("##cross", ImVec2(-1, em * 14)):
            implot.setup_axes("x", "Amplitude")
            max_amp = max(np.max(np.abs(field)), 0.01)
            implot.setup_axes_limits(
                float(xs[0]), float(xs[-1]),
                float(-max_amp * 1.1), float(max_amp * 1.4),
                imgui.Cond_.always)
            implot.plot_line("Wave", xs, cross)
            implot.end_plot()
    imgui.text(f"FPS: {hello_imgui.frame_rate():.1f}")

    imgui.end_child()

    imgui.same_line()

    # Wave field (right area)
    imgui.begin_child("field", ImVec2(0, 0))
    avail = imgui.get_content_region_avail()
    field_size = min(avail.x, avail.y) - em
    origin = imgui.get_cursor_screen_pos()
    # Center the field
    offset_x = (avail.x - field_size) * 0.5
    offset_y = (avail.y - field_size) * 0.5
    field_origin = ImVec2(origin.x + offset_x, origin.y + offset_y)
    field_dim = ImVec2(field_size, field_size)

    draw_wave_field(state, field_origin, field_dim)
    handle_source_dragging(state, field_origin, field_dim)

    # Play/Pause overlay button at bottom-center of the wave field
    btn_w, btn_h = em * 3, em * 2
    btn_x = field_origin.x + field_size * 0.5 - btn_w * 0.5
    btn_y = field_origin.y + field_size - btn_h - em * 0.5
    imgui.set_cursor_screen_pos(ImVec2(btn_x, btn_y))
    imgui.push_style_var(imgui.StyleVar_.frame_rounding, em * 3.0)
    imgui.push_style_color(imgui.Col_.button, ImVec4(0.15, 0.15, 0.15, 0.6))
    imgui.push_style_color(imgui.Col_.button_hovered, ImVec4(0.25, 0.25, 0.25, 0.8))
    imgui.push_style_color(imgui.Col_.button_active, ImVec4(0.35, 0.35, 0.35, 0.9))
    if imgui.button(FA_PAUSE if not state.paused else FA_PLAY, ImVec2(btn_w, btn_h)):
        state.paused = not state.paused
    imgui.pop_style_color(3)
    imgui.pop_style_var()

    imgui.end_child()


def main():
    state = AppState()
    immapp.run(
        lambda: gui(state),
        window_title="Wave Interference",
        window_size=(1200, 750),
        with_implot=True,
        with_markdown=True,
        fps_idle=0,
    )


if __name__ == "__main__":
    main()
