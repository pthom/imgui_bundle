# type: ignore
"""
Double pendulum, native via Dear ImGui Bundle (ImGui + ImPlot + immapp).

Run with:
    python pendulum_bundle.py

Same features as the NiceGUI version (speed slider, pause, trails, reset,
pendulum view, energy plot), rendered natively at the display refresh rate.
"""
import numpy as np
from imgui_bundle import imgui, immapp, implot


def derivs(s, m1, m2, l1, l2, g):
    th1, w1, th2, w2 = s
    d = th2 - th1
    den1 = (m1 + m2) * l1 - m2 * l1 * np.cos(d) ** 2
    den2 = (l2 / l1) * den1
    dw1 = (m2 * l1 * w1 ** 2 * np.sin(d) * np.cos(d) +
           m2 * g * np.sin(th2) * np.cos(d) +
           m2 * l2 * w2 ** 2 * np.sin(d) -
           (m1 + m2) * g * np.sin(th1)) / den1
    dw2 = (-m2 * l2 * w2 ** 2 * np.sin(d) * np.cos(d) +
           (m1 + m2) * g * np.sin(th1) * np.cos(d) -
           (m1 + m2) * l1 * w1 ** 2 * np.sin(d) -
           (m1 + m2) * g * np.sin(th2)) / den2
    return np.array([w1, dw1, w2, dw2])


def rk4(s, dt, *a):
    k1 = derivs(s, *a)
    k2 = derivs(s + 0.5 * dt * k1, *a)
    k3 = derivs(s + 0.5 * dt * k2, *a)
    k4 = derivs(s + dt * k3, *a)
    return s + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


M1, M2, L1, L2, G = 1.0, 1.0, 1.0, 1.0, 9.81
INIT = np.array([np.pi * 0.75, 0.0, np.pi * 0.75, 0.0])

state = INIT.copy()
frame = 0
speed = 1.0
paused = False
trails = True
trail_x: list[float] = []
trail_y: list[float] = []
energy_t: list[int] = []
energy_ke: list[float] = []
energy_pe: list[float] = []


def gui():
    global state, frame, speed, paused, trails

    imgui.begin_child("controls", imgui.ImVec2(220, 0))
    _, speed = imgui.slider_float("Speed", speed, 0.1, 3.0)
    _, paused = imgui.checkbox("Pause", paused)
    _, trails = imgui.checkbox("Trails", trails)
    if imgui.button("Reset"):
        state = INIT.copy(); frame = 0
        trail_x.clear(); trail_y.clear()
        energy_t.clear(); energy_ke.clear(); energy_pe.clear()
    imgui.end_child()
    imgui.same_line()
    imgui.begin_child("plots")

    if not paused:
        state = rk4(state, 0.02 * speed, M1, M2, L1, L2, G)
        frame += 1
        th1, w1, th2, w2 = state
        x2_phys = L1 * np.sin(th1) + L2 * np.sin(th2)
        y2_phys = L1 * np.cos(th1) + L2 * np.cos(th2)
        if trails:
            trail_x.append(x2_phys); trail_y.append(y2_phys)
            if len(trail_x) > 300:
                del trail_x[:-300]; del trail_y[:-300]
        v1_sq = (L1 * w1) ** 2
        v2_sq = v1_sq + (L2 * w2) ** 2 + 2 * L1 * L2 * w1 * w2 * np.cos(th1 - th2)
        energy_t.append(frame)
        energy_ke.append(0.5 * M1 * v1_sq + 0.5 * M2 * v2_sq)
        energy_pe.append(-(M1 + M2) * G * L1 * np.cos(th1) - M2 * G * L2 * np.cos(th2))
        if len(energy_t) > 500:
            del energy_t[:-500]; del energy_ke[:-500]; del energy_pe[:-500]

    th1, _, th2, _ = state
    x1, y1 = L1 * np.sin(th1), L1 * np.cos(th1)
    x2, y2 = x1 + L2 * np.sin(th2), y1 + L2 * np.cos(th2)

    avail = imgui.get_content_region_avail()
    cw, ch = avail.x, avail.y - 220
    p0 = imgui.get_cursor_screen_pos()
    imgui.dummy(imgui.ImVec2(cw, ch))
    dl = imgui.get_window_draw_list()
    u32 = imgui.color_convert_float4_to_u32

    def to_px(x, y):
        return imgui.ImVec2(p0.x + (x + 2.5) / 5.0 * cw,
                            p0.y + (1.5 - y) / 4.0 * ch)

    dl.add_rect(p0, imgui.ImVec2(p0.x + cw, p0.y + ch),
                u32(imgui.ImVec4(0.4, 0.4, 0.4, 1.0)))
    if trails and len(trail_x) > 1:
        dl.add_polyline([to_px(trail_x[i], trail_y[i]) for i in range(len(trail_x))],
                        u32(imgui.ImVec4(1.0, 0.5, 0.0, 0.5)), 1.0, 0)
    rod = u32(imgui.ImVec4(0.8, 0.8, 0.8, 1.0))
    dl.add_line(to_px(0, 0), to_px(x1, y1), rod, 3.0)
    dl.add_line(to_px(x1, y1), to_px(x2, y2), rod, 3.0)
    bob = u32(imgui.ImVec4(1.0, 0.5, 0.0, 1.0))
    dl.add_circle_filled(to_px(x1, y1), 8.0, bob)
    dl.add_circle_filled(to_px(x2, y2), 8.0, bob)

    if implot.begin_plot("Energy", imgui.ImVec2(-1, 200)):
        implot.setup_axes("frame", "energy",
                          implot.AxisFlags_.auto_fit.value,
                          implot.AxisFlags_.auto_fit.value)
        if len(energy_t) > 1:
            implot.plot_line("KE", np.asarray(energy_t, float), np.asarray(energy_ke),
                             implot.Spec(line_color=imgui.ImVec4(0.25, 0.41, 0.88, 1.0)))
            implot.plot_line("PE", np.asarray(energy_t, float), np.asarray(energy_pe),
                             implot.Spec(line_color=imgui.ImVec4(0.86, 0.08, 0.24, 1.0)))
        implot.end_plot()

    imgui.end_child()


if __name__ == "__main__":
    immapp.run(gui_function=gui, window_title="Double pendulum (ImGui Bundle)",
               window_size=(900, 720), with_implot=True, fps_idle=0)
