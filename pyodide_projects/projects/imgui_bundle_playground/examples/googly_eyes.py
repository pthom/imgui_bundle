"""Googly Eyes: they follow your mouse!
Inspired by the ImDrawList coding party
(github.com/ocornut/imgui/issues/3606)."""

import math
from imgui_bundle import imgui, immapp, hello_imgui, imgui_knobs, imgui_toggle, ImVec4

# State
eye_color = ImVec4(0.3, 0.6, 1.0, 1.0)
pupil_ratio = 0.5
cross_eyed = False


def draw_eye(draw_list: imgui.ImDrawList, center: imgui.ImVec2, rx: float, ry: float,
             mouse: imgui.ImVec2, pupil_r: float, iris_col: int):
    """Draw one googly eye that tracks the mouse."""
    # Eyeball
    draw_list.add_ellipse_filled(center, (rx, ry), 0xFFFFFFFF)
    draw_list.add_ellipse(center, (rx, ry), 0xFF000000, thickness=2.0)

    # Compute pupil position: follow mouse, constrained inside eye
    dx, dy = mouse.x - center.x, mouse.y - center.y
    # Normalize to ellipse space
    nx, ny = dx / max(rx - pupil_r, 1), dy / max(ry - pupil_r, 1)
    dist = math.sqrt(nx * nx + ny * ny)
    if dist > 1.0:
        nx, ny = nx / dist, ny / dist
    px = center.x + nx * (rx - pupil_r)
    py = center.y + ny * (ry - pupil_r)

    # Iris + pupil
    draw_list.add_circle_filled((px, py), pupil_r, iris_col)
    draw_list.add_circle_filled((px, py), pupil_r * 0.5, 0xFF000000)
    # Glint
    draw_list.add_circle_filled((px - pupil_r * 0.25, py - pupil_r * 0.3), pupil_r * 0.18, 0xFFFFFFFF)


def gui():
    global eye_color, pupil_ratio, cross_eyed

    em = hello_imgui.em_size()
    mouse = imgui.get_mouse_pos()

    # Canvas
    canvas_w, canvas_h = em * 20, em * 12
    cursor = imgui.get_cursor_screen_pos()
    draw_list = imgui.get_window_draw_list()

    # Eye geometry
    eye_rx, eye_ry = em * 3.0, em * 4.0
    spacing = em * 3.5
    center_y = cursor.y + canvas_h * 0.5
    left_eye = imgui.ImVec2(cursor.x + canvas_w * 0.5 - spacing, center_y)
    right_eye = imgui.ImVec2(cursor.x + canvas_w * 0.5 + spacing, center_y)
    pupil_r = eye_rx * pupil_ratio

    iris_col = imgui.color_convert_float4_to_u32(eye_color)

    # If cross-eyed, each eye looks at the other eye's center
    cross_eye_ratio = 0.7
    left_target = (right_eye * cross_eye_ratio + mouse * (1 - cross_eye_ratio)) if cross_eyed else mouse
    right_target = (left_eye * cross_eye_ratio + mouse * (1 - cross_eye_ratio)) if cross_eyed else mouse

    draw_eye(draw_list, left_eye, eye_rx, eye_ry, left_target, pupil_r, iris_col)
    draw_eye(draw_list, right_eye, eye_rx, eye_ry, right_target, pupil_r, iris_col)
    imgui.dummy((canvas_w, canvas_h))

    # Controls
    imgui.set_next_item_width(em * 8)
    _, eye_color = imgui.color_edit4("Iris Color", eye_color, imgui.ColorEditFlags_.no_inputs)

    imgui.same_line()
    _, cross_eyed = imgui_toggle.toggle("Cross-eyed", cross_eyed, imgui_toggle.ToggleFlags_.animated)

    _, pupil_ratio = imgui_knobs.knob(
        "Pupil Size", pupil_ratio, 0.15, 1.1, variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot, size=40)


if __name__ == "__main__":
    immapp.run(gui, window_size=(380, 420), window_title="Googly Eyes!", fps_idle=0)
