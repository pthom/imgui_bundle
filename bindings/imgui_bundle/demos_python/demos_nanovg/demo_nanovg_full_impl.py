# Port of bindings/imgui_bundle/demos_cpp/demos_nanovg/demo_nanovg_full/demo_nanovg_full_impl.cpp
from imgui_bundle import nanovg as nvg, hello_imgui

from typing import List

import math


###############################################################################
# API: port of demo_nanovg_full_impl.h
###############################################################################
class DemoData:
    fontNormal: int
    fontBold: int
    fontIcons: int
    fontEmoji: int
    images: List[int]

    def __init__(self):
        self.images = [-1] * 12


# def load_demo_data(vg: nvg.Context) -> DemoData:
#     pass
#
#
# def free_demo_data(vg: nvg.Context, data: DemoData) -> None:
#     pass
#
#
# def render_demo(vg: nvg.Context, data: DemoData, mx: float, my: float, width: float, height: float, t: float, blowup: bool) -> None:
#     pass


###############################################################################
# port of demo_nanovg_full_impl.cpp
###############################################################################
ICON_SEARCH = chr(0x1F50D)
ICON_CIRCLED_CROSS = chr(0x2716)
ICON_CHEVRON_RIGHT = chr(0xE75E)
ICON_CHECK = chr(0x2713)
ICON_LOGIN = chr(0xE740)
ICON_TRASH = chr(0xE729)


def clamp(x: float, mn: float, mx: float) -> float:
    return min(max(x, mn), mx)


def is_black(c: nvg.Color) -> bool:
    return c.r == 0.0 and c.g == 0.0 and c.b == 0.0 and c.a == 1.0


def draw_window(vg: nvg.Context, title: str, x: float, y: float, w: float, h: float) -> None:
    cornerRadius = 3.0

    nvg.save(vg)

    # Window
    nvg.begin_path(vg)
    nvg.rounded_rect(vg, x, y, w, h, cornerRadius)
    nvg.fill_color(vg, nvg.rgba(28, 30, 34, 192))
    nvg.fill(vg)

    # Drop shadow
    shadowPaint = nvg.box_gradient(vg, x, y + 2, w, h, cornerRadius * 2, 10, nvg.rgba(0, 0, 0, 128), nvg.rgba(0, 0, 0, 0))
    nvg.begin_path(vg)
    nvg.rect(vg, x - 10, y - 10, w + 20, h + 30)
    nvg.rounded_rect(vg, x, y, w, h, cornerRadius)
    nvg.path_winding(vg, nvg.Winding.cw.value)
    nvg.fill_paint(vg, shadowPaint)
    nvg.fill(vg)

    # Header
    headerPaint = nvg.linear_gradient(vg, x, y, x, y + 15, nvg.rgba(255, 255, 255, 8), nvg.rgba(0, 0, 0, 16))
    nvg.begin_path(vg)
    nvg.rounded_rect(vg, x + 1, y + 1, w - 2, 30, cornerRadius - 1)
    nvg.fill_paint(vg, headerPaint)
    nvg.fill(vg)
    nvg.begin_path(vg)
    nvg.move_to(vg, x + 0.5, y + 0.5 + 30)
    nvg.line_to(vg, x + 0.5 + w - 1, y + 0.5 + 30)
    nvg.stroke_color(vg, nvg.rgba(0, 0, 0, 32))
    nvg.stroke(vg)

    nvg.font_size(vg, 18.0)
    nvg.font_face(vg, "sans-bold")
    nvg.text_align(vg, nvg.Align.align_center.value | nvg.Align.align_middle.value)

    nvg.font_blur(vg, 2)
    nvg.fill_color(vg, nvg.rgba(0, 0, 0, 128))
    nvg.text(vg, x + w / 2, y + 16 + 1, title)

    nvg.font_blur(vg, 0)
    nvg.fill_color(vg, nvg.rgba(220, 220, 220, 160))
    nvg.text(vg, x + w / 2, y + 16, title)

    nvg.restore(vg)


def draw_search_box(vg: nvg.Context, text: str, x: float, y: float, w: float, h: float) -> None:
    cornerRadius = h / 2 - 1

    # Edit
    bg = nvg.box_gradient(vg, x, y + 1.5, w, h, h / 2, 5, nvg.rgba(0, 0, 0, 16), nvg.rgba(0, 0, 0, 92))
    nvg.begin_path(vg)
    nvg.rounded_rect(vg, x, y, w, h, cornerRadius)
    nvg.fill_paint(vg, bg)
    nvg.fill(vg)

    nvg.font_size(vg, h * 1.3)
    nvg.font_face(vg, "icons")
    nvg.fill_color(vg, nvg.rgba(255, 255, 255, 64))
    nvg.text_align(vg, nvg.Align.align_center.value | nvg.Align.align_middle.value)
    nvg.text(vg, x + h * 0.55, y + h * 0.55, ICON_SEARCH)

    nvg.font_size(vg, 20.0)
    nvg.font_face(vg, "sans")
    nvg.fill_color(vg, nvg.rgba(255, 255, 255, 32))

    nvg.text_align(vg, nvg.Align.align_left.value | nvg.Align.align_middle.value)
    nvg.text(vg, x + h * 1.05, y + h * 0.5, text)

    nvg.font_size(vg, h * 1.3)
    nvg.font_face(vg, "icons")
    nvg.fill_color(vg, nvg.rgba(255, 255, 255, 32))
    nvg.text_align(vg, nvg.Align.align_center.value | nvg.Align.align_middle.value)
    nvg.text(vg, x + w - h * 0.55, y + h * 0.55, ICON_CIRCLED_CROSS)


def draw_drop_down(vg: nvg.Context, text: str, x: float, y: float, w: float, h: float) -> None:
    cornerRadius = 4.0

    bg = nvg.linear_gradient(vg, x, y, x, y + h, nvg.rgba(255, 255, 255, 16), nvg.rgba(0, 0, 0, 16))
    nvg.begin_path(vg)
    nvg.rounded_rect(vg, x + 1, y + 1, w - 2, h - 2, cornerRadius - 1)
    nvg.fill_paint(vg, bg)
    nvg.fill(vg)

    nvg.begin_path(vg)
    nvg.rounded_rect(vg, x + 0.5, y + 0.5, w - 1, h - 1, cornerRadius - 0.5)
    nvg.stroke_color(vg, nvg.rgba(0, 0, 0, 48))
    nvg.stroke(vg)

    nvg.font_size(vg, 20.0)
    nvg.font_face(vg, "sans")
    nvg.fill_color(vg, nvg.rgba(255, 255, 255, 160))
    nvg.text_align(vg, nvg.Align.align_left.value | nvg.Align.align_middle.value)
    nvg.text(vg, x + h * 0.3, y + h * 0.5, text)

    nvg.font_size(vg, h * 1.3)
    nvg.font_face(vg, "icons")
    nvg.fill_color(vg, nvg.rgba(255, 255, 255, 64))
    nvg.text_align(vg, nvg.Align.align_center.value | nvg.Align.align_middle.value)
    nvg.text(vg, x + w - h * 0.5, y + h * 0.5, ICON_CHEVRON_RIGHT)


def draw_label(vg: nvg.Context, text: str, x: float, y: float, w: float, h: float) -> None:
    nvg.font_size(vg, 18.0)
    nvg.font_face(vg, "sans")
    nvg.fill_color(vg, nvg.rgba(255, 255, 255, 128))

    nvg.text_align(vg, nvg.Align.align_left.value | nvg.Align.align_middle.value)
    nvg.text(vg, x, y + h * 0.5, text)


def draw_edit_box_base(vg: nvg.Context, x: float, y: float, w: float, h: float) -> None:
    # Edit
    bg = nvg.box_gradient(vg, x + 1, y + 1 + 1.5, w - 2, h - 2, 3, 4, nvg.rgba(255, 255, 255, 32), nvg.rgba(32, 32, 32, 32))
    nvg.begin_path(vg)
    nvg.rounded_rect(vg, x + 1, y + 1, w - 2, h - 2, 4 - 1)
    nvg.fill_paint(vg, bg)
    nvg.fill(vg)

    nvg.begin_path(vg)
    nvg.rounded_rect(vg, x + 0.5, y + 0.5, w - 1, h - 1, 4 - 0.5)
    nvg.stroke_color(vg, nvg.rgba(0, 0, 0, 48))
    nvg.stroke(vg)


def draw_edit_box(vg: nvg.Context, text: str, x: float, y: float, w: float, h: float) -> None:
    draw_edit_box_base(vg, x, y, w, h)

    nvg.font_size(vg, 20.0)
    nvg.font_face(vg, "sans")
    nvg.fill_color(vg, nvg.rgba(255, 255, 255, 64))
    nvg.text_align(vg, nvg.Align.align_left.value | nvg.Align.align_middle.value)
    nvg.text(vg, x + h * 0.3, y + h * 0.5, text)


def draw_edit_box_num(vg: nvg.Context, text: str, units: str, x: float, y: float, w: float, h: float) -> None:
    draw_edit_box_base(vg, x, y, w, h)

    nvg.font_size(vg, 18.0)
    nvg.font_face(vg, "sans")
    nvg.fill_color(vg, nvg.rgba(255, 255, 255, 64))
    nvg.text_align(vg, nvg.Align.align_right.value | nvg.Align.align_middle.value)
    nvg.text(vg, x + w - h * 0.3, y + h * 0.5, units)

    nvg.font_size(vg, 20.0)
    nvg.font_face(vg, "sans")
    nvg.fill_color(vg, nvg.rgba(255, 255, 255, 128))
    nvg.text_align(vg, nvg.Align.align_right.value | nvg.Align.align_middle.value)
    nvg.text(vg, x + w - h * 0.5, y + h * 0.5, text)


def draw_check_box(vg: nvg.Context, text: str, x: float, y: float, w: float, h: float) -> None:
    nvg.font_size(vg, 18.0)
    nvg.font_face(vg, "sans")
    nvg.fill_color(vg, nvg.rgba(255, 255, 255, 160))

    nvg.text_align(vg, nvg.Align.align_left.value | nvg.Align.align_middle.value)
    nvg.text(vg, x + 28, y + h * 0.5, text)

    bg = nvg.box_gradient(vg, x + 1, y + int(h * 0.5) - 9 + 1, 18, 18, 3, 3, nvg.rgba(0, 0, 0, 32), nvg.rgba(0, 0, 0, 92))
    nvg.begin_path(vg)
    nvg.rounded_rect(vg, x + 1, y + int(h * 0.5) - 9, 18, 18, 3)
    nvg.fill_paint(vg, bg)
    nvg.fill(vg)

    nvg.font_size(vg, 40)
    nvg.font_face(vg, "icons")
    nvg.fill_color(vg, nvg.rgba(255, 255, 255, 128))
    nvg.text_align(vg, nvg.Align.align_center.value | nvg.Align.align_middle.value)
    nvg.text(vg, x + 9 + 2, y + h * 0.5, ICON_CHECK)


def draw_button(vg: nvg.Context, preicon: str, text: str, x: float, y: float, w: float, h: float, col: nvg.Color) -> None:
    cornerRadius = 4.0
    tw = 0.0
    iw = 0.0

    bg = nvg.linear_gradient(vg, x, y, x, y + h, nvg.rgba(255, 255, 255, is_black(col) and 16 or 32), nvg.rgba(0, 0, 0, is_black(col) and 16 or 32))
    nvg.begin_path(vg)
    nvg.rounded_rect(vg, x + 1, y + 1, w - 2, h - 2, cornerRadius - 1)
    if not is_black(col):
        nvg.fill_color(vg, col)
        nvg.fill(vg)
    nvg.fill_paint(vg, bg)
    nvg.fill(vg)

    nvg.begin_path(vg)
    nvg.rounded_rect(vg, x + 0.5, y + 0.5, w - 1, h - 1, cornerRadius - 0.5)
    nvg.stroke_color(vg, nvg.rgba(0, 0, 0, 48))
    nvg.stroke(vg)

    nvg.font_size(vg, 20.0)
    nvg.font_face(vg, "sans-bold")
    _, tw = nvg.text_bounds(vg, 0, 0, text)
    if preicon != "":
        nvg.font_size(vg, h * 1.3)
        nvg.font_face(vg, "icons")
        _, iw = nvg.text_bounds(vg, 0, 0, preicon)
        iw += h * 0.15

    if preicon != "":
        nvg.font_size(vg, h * 1.3)
        nvg.font_face(vg, "icons")
        nvg.fill_color(vg, nvg.rgba(255, 255, 255, 96))
        nvg.text_align(vg, nvg.Align.align_left.value | nvg.Align.align_middle.value)
        nvg.text(vg, x + w * 0.5 - tw * 0.5 - iw * 0.75, y + h * 0.5, preicon)

    nvg.font_size(vg, 20.0)
    nvg.font_face(vg, "sans-bold")
    nvg.text_align(vg, nvg.Align.align_left.value | nvg.Align.align_middle.value)
    nvg.fill_color(vg, nvg.rgba(0, 0, 0, 160))
    nvg.text(vg, x + w * 0.5 - tw * 0.5 + iw * 0.25, y + h * 0.5 - 1, text)
    nvg.fill_color(vg, nvg.rgba(255, 255, 255, 160))
    nvg.text(vg, x + w * 0.5 - tw * 0.5 + iw * 0.25, y + h * 0.5, text)


def draw_slider(vg: nvg.Context, pos: float, x: float, y: float, w: float, h: float) -> None:
    cy = y + (int)(h * 0.5)
    kr = (int)(h * 0.25)

    nvg.save(vg)
    #nvg.clear_state(vg)

    # Slot
    bg = nvg.box_gradient(vg, x, cy - 2 + 1, w, 4, 2, 2, nvg.rgba(0, 0, 0, 32), nvg.rgba(0, 0, 0, 128))
    nvg.begin_path(vg)
    nvg.rounded_rect(vg, x, cy - 2, w, 4, 2)
    nvg.fill_paint(vg, bg)
    nvg.fill(vg)

    # Knob Shadow
    bg = nvg.radial_gradient(vg, x + (int)(pos * w), cy + 1, kr - 3, kr + 3, nvg.rgba(0, 0, 0, 64), nvg.rgba(0, 0, 0, 0))
    nvg.begin_path(vg)
    nvg.rect(vg, x + (int)(pos * w) - kr - 5, cy - kr - 5, kr * 2 + 5 + 5, kr * 2 + 5 + 5 + 3)
    nvg.circle(vg, x + (int)(pos * w), cy, kr)
    nvg.path_winding(vg, nvg.Solidity.hole.value)
    nvg.fill_paint(vg, bg)
    nvg.fill(vg)

    # Knob
    knob = nvg.linear_gradient(vg, x, cy - kr, x, cy + kr, nvg.rgba(255, 255, 255, 16), nvg.rgba(0, 0, 0, 16))
    nvg.begin_path(vg)
    nvg.circle(vg, x + (int)(pos * w), cy, kr - 1)
    nvg.fill_color(vg, nvg.rgba(40, 43, 48, 255))
    nvg.fill(vg)
    nvg.fill_paint(vg, knob)
    nvg.fill(vg)

    nvg.begin_path(vg)
    nvg.circle(vg, x + (int)(pos * w), cy, kr - 0.5)
    nvg.stroke_color(vg, nvg.rgba(0, 0, 0, 92))
    nvg.stroke(vg)

    nvg.restore(vg)


def draw_eyes(vg: nvg.Context, x: float, y: float, w: float, h: float, mx: float, my: float, t: float) -> None:
    ex = w * 0.23
    ey = h * 0.5
    lx = x + ex
    ly = y + ey
    rx = x + w - ex
    ry = y + ey
    br = (ex < ey and ex or ey) * 0.5
    blink = 1 - math.pow(math.sin(t * 0.5), 200) * 0.8

    bg = nvg.linear_gradient(vg, x, y + h * 0.5, x + w * 0.1, y + h, nvg.rgba(0, 0, 0, 32), nvg.rgba(0, 0, 0, 16))
    nvg.begin_path(vg)
    nvg.ellipse(vg, lx + 3.0, ly + 16.0, ex, ey)
    nvg.ellipse(vg, rx + 3.0, ry + 16.0, ex, ey)
    nvg.fill_paint(vg, bg)
    nvg.fill(vg)

    bg = nvg.linear_gradient(vg, x, y + h * 0.25, x + w * 0.1, y + h, nvg.rgba(220, 220, 220, 255), nvg.rgba(128, 128, 128, 255))
    nvg.begin_path(vg)
    nvg.ellipse(vg, lx, ly, ex, ey)
    nvg.ellipse(vg, rx, ry, ex, ey)
    nvg.fill_paint(vg, bg)
    nvg.fill(vg)

    dx = (mx - rx) / (ex * 10)
    dy = (my - ry) / (ey * 10)
    d = math.sqrt(dx * dx + dy * dy)
    if d > 1.0:
        dx /= d
        dy /= d
    dx *= ex * 0.4
    dy *= ey * 0.5
    nvg.begin_path(vg)
    nvg.ellipse(vg, lx + dx, ly + dy + ey * 0.25 * (1 - blink), br, br * blink)
    nvg.fill_color(vg, nvg.rgba(32, 32, 32, 255))
    nvg.fill(vg)

    dx = (mx - rx) / (ex * 10)
    dy = (my - ry) / (ey * 10)
    d = math.sqrt(dx * dx + dy * dy)
    if d > 1.0:
        dx /= d
        dy /= d
    dx *= ex * 0.4
    dy *= ey * 0.5
    nvg.begin_path(vg)
    nvg.ellipse(vg, rx + dx, ry + dy + ey * 0.25 * (1 - blink), br, br * blink)
    nvg.fill_color(vg, nvg.rgba(32, 32, 32, 255))
    nvg.fill(vg)

    dx = (mx - rx) / (ex * 10)
    dy = (my - ry) / (ey * 10)
    d = math.sqrt(dx * dx + dy * dy)
    if d > 1.0:
        dx /= d
        dy /= d
    dx *= ex * 0.4
    dy *= ey * 0.5
    nvg.begin_path(vg)
    nvg.ellipse(vg, lx + dx, ly + dy + ey * 0.25 * (1 - blink), br * 0.5, br * blink)
    nvg.fill_color(vg, nvg.rgba(32, 32, 32, 255))
    nvg.fill(vg)

    gloss = nvg.radial_gradient(vg, lx - ex * 0.25, ly - ey * 0.5, ex * 0.1, ex * 0.75, nvg.rgba(255, 255, 255, 128), nvg.rgba(255, 255, 255, 0))
    nvg.begin_path(vg)
    nvg.ellipse(vg, lx, ly, ex, ey)
    nvg.fill_paint(vg, gloss)
    nvg.fill(vg)

    gloss = nvg.radial_gradient(vg, rx - ex * 0.25, ry - ey * 0.5, ex * 0.1, ex * 0.75, nvg.rgba(255, 255, 255, 128), nvg.rgba(255, 255, 255, 0))
    nvg.begin_path(vg)
    nvg.ellipse(vg, rx, ry, ex, ey)
    nvg.fill_paint(vg, gloss)
    nvg.fill(vg)


def draw_graph(vg: nvg.Context, x: float, y: float, w: float, h: float, t: float) -> None:
    samples = [0.0] * 6
    sx = [0.0] * 6
    sy = [0.0] * 6
    dx = w / 5.0

    samples[0] = (1 + math.sin(t * 1.2345 + math.cos(t * 0.33457) * 0.44)) * 0.5
    samples[1] = (1 + math.sin(t * 0.68363 + math.cos(t * 1.3) * 1.55)) * 0.5
    samples[2] = (1 + math.sin(t * 1.1642 + math.cos(t * 0.33457) * 1.24)) * 0.5
    samples[3] = (1 + math.sin(t * 0.56345 + math.cos(t * 1.63) * 0.14)) * 0.5
    samples[4] = (1 + math.sin(t * 1.6245 + math.cos(t * 0.254) * 0.3)) * 0.5
    samples[5] = (1 + math.sin(t * 0.345 + math.cos(t * 0.03) * 0.6)) * 0.5

    for i in range(6):
        sx[i] = x + i * dx
        sy[i] = y + h * samples[i] * 0.8

    # Graph background
    bg = nvg.linear_gradient(vg, x, y, x, y + h, nvg.rgba(0, 160, 192, 0), nvg.rgba(0, 160, 192, 64))
    nvg.begin_path(vg)
    nvg.move_to(vg, sx[0], sy[0])
    for i in range(1, 6):
        nvg.bezier_to(vg, sx[i - 1] + dx * 0.5, sy[i - 1], sx[i] - dx * 0.5, sy[i], sx[i], sy[i])
    nvg.line_to(vg, x + w, y + h)
    nvg.line_to(vg, x, y + h)
    nvg.fill_paint(vg, bg)
    nvg.fill(vg)

    # Graph line
    nvg.begin_path(vg)
    nvg.move_to(vg, sx[0], sy[0] + 2)
    for i in range(1, 6):
        nvg.bezier_to(vg, sx[i - 1] + dx * 0.5, sy[i - 1] + 2, sx[i] - dx * 0.5, sy[i] + 2, sx[i], sy[i] + 2)
    nvg.stroke_color(vg, nvg.rgba(0, 0, 0, 32))
    nvg.stroke_width(vg, 3.0)
    nvg.stroke(vg)

    # Graph sample pos
    for i in range(6):
        bg = nvg.radial_gradient(vg, sx[i], sy[i] + 2, 3.0, 8.0, nvg.rgba(0, 0, 0, 32), nvg.rgba(0, 0, 0, 0))
        nvg.begin_path(vg)
        nvg.rect(vg, sx[i] - 10, sy[i] - 10 + 2, 20, 20)
        nvg.fill_paint(vg, bg)
        nvg.fill(vg)

    nvg.begin_path(vg)
    for i in range(6):
        nvg.circle(vg, sx[i], sy[i], 4.0)
    nvg.fill_color(vg, nvg.rgba(0, 160, 192, 255))
    nvg.fill(vg)
    nvg.begin_path(vg)
    for i in range(6):
        nvg.circle(vg, sx[i], sy[i], 2.0)
    nvg.fill_color(vg, nvg.rgba(220, 220, 220, 255))
    nvg.fill(vg)

    nvg.stroke_width(vg, 1.0)


def draw_spinner(vg: nvg.Context, cx: float, cy: float, r: float, t: float) -> None:
    a0 = 0.0 + t * 6
    a1 = math.pi + t * 6
    r0 = r
    r1 = r * 0.75
    nvg.save(vg)
    nvg.begin_path(vg)
    nvg.arc(vg, cx, cy, r0, a0, a1, nvg.Winding.cw.value)
    nvg.arc(vg, cx, cy, r1, a1, a0, nvg.Winding.ccw.value)
    nvg.close_path(vg)
    ax = cx + math.cos(a0) * (r0 + r1) * 0.5
    ay = cy + math.sin(a0) * (r0 + r1) * 0.5
    bx = cx + math.cos(a1) * (r0 + r1) * 0.5
    by = cy + math.sin(a1) * (r0 + r1) * 0.5
    paint = nvg.linear_gradient(vg, ax, ay, bx, by, nvg.rgba(0, 0, 0, 0), nvg.rgba(0, 0, 0, 128))
    nvg.fill_paint(vg, paint)
    nvg.fill(vg)
    nvg.restore(vg)


def draw_thumbnails(vg: nvg.Context, x: float, y: float, w: float, h: float, images: List[int], nimages: int, t: float) -> None:
    cornerRadius = 3.0
    thumb = 60.0
    arry = 30.5
    stackh = (nimages / 2) * (thumb + 10) + 10
    u = (1 + math.cos(t * 0.5)) * 0.5
    u2 = (1 - math.cos(t * 0.2)) * 0.5

    nvg.save(vg)
    #nvg.clear_state(vg)

    # Drop shadow
    shadowPaint = nvg.box_gradient(vg, x, y + 4, w, h, cornerRadius * 2, 20, nvg.rgba(0, 0, 0, 128), nvg.rgba(0, 0, 0, 0))
    nvg.begin_path(vg)
    nvg.rect(vg, x - 10, y - 10, w + 20, h + 30)
    nvg.rounded_rect(vg, x, y, w, h, cornerRadius)
    nvg.path_winding(vg, nvg.Winding.cw.value)
    nvg.fill_paint(vg, shadowPaint)
    nvg.fill(vg)

    # Window
    nvg.begin_path(vg)
    nvg.rounded_rect(vg, x, y, w, h, cornerRadius)
    nvg.move_to(vg, x - 10, y + arry)
    nvg.line_to(vg, x + 1, y + arry - 11)
    nvg.line_to(vg, x + 1, y + arry + 11)
    nvg.fill_color(vg, nvg.rgba(200, 200, 200, 255))
    nvg.fill(vg)

    nvg.save(vg)
    nvg.scissor(vg, x, y, w, h)
    nvg.translate(vg, 0, -(stackh - h) * u)

    dv = 1.0 / (nimages - 1)

    for i in range(nimages):
        tx = x + 10
        ty = y + 10
        tx += (i % 2) * (thumb + 10)
        ty += (i / 2) * (thumb + 10)
        imgw, imgh = nvg.image_size(vg, images[i])
        if imgw < imgh:
            iw = thumb
            ih = iw * imgh / imgw
            ix = 0
            iy = -(ih - thumb) * 0.5
        else:
            ih = thumb
            iw = ih * imgw / imgh
            ix = -(iw - thumb) * 0.5
            iy = 0

        v = i * dv
        a = clamp((u2 - v) / dv, 0, 1)

        if a < 1.0:
            draw_spinner(vg, tx + thumb / 2, ty + thumb / 2, thumb * 0.25, t)

        imgPaint = nvg.image_pattern(vg, tx + ix, ty + iy, iw, ih, 0.0 / 180.0 * math.pi, images[i], a)
        nvg.begin_path(vg)
        nvg.rounded_rect(vg, tx, ty, thumb, thumb, 5)
        nvg.fill_paint(vg, imgPaint)
        nvg.fill(vg)

        shadowPaint = nvg.box_gradient(vg, tx - 1, ty, thumb + 2, thumb + 2, 5, 3, nvg.rgba(0, 0, 0, 128), nvg.rgba(0, 0, 0, 0))
        nvg.begin_path(vg)
        nvg.rect(vg, tx - 5, ty - 5, thumb + 10, thumb + 10)
        nvg.rounded_rect(vg, tx, ty, thumb, thumb, 6)
        nvg.path_winding(vg, nvg.Solidity.hole.value)
        nvg.fill_paint(vg, shadowPaint)
        nvg.fill(vg)

        nvg.begin_path(vg)
        nvg.rounded_rect(vg, tx + 0.5, ty + 0.5, thumb - 1, thumb - 1, 4 - 0.5)
        nvg.stroke_width(vg, 1.0)
        nvg.stroke_color(vg, nvg.rgba(255, 255, 255, 192))
        nvg.stroke(vg)

    nvg.restore(vg)

    # Hide fades
    fadePaint = nvg.linear_gradient(vg, x, y, x, y + 6, nvg.rgba(200, 200, 200, 255), nvg.rgba(200, 200, 200, 0))
    nvg.begin_path(vg)
    nvg.rect(vg, x + 4, y, w - 8, 6)
    nvg.fill_paint(vg, fadePaint)
    nvg.fill(vg)

    fadePaint = nvg.linear_gradient(vg, x, y + h, x, y + h - 6, nvg.rgba(200, 200, 200, 255), nvg.rgba(200, 200, 200, 0))
    nvg.begin_path(vg)
    nvg.rect(vg, x + 4, y + h - 6, w - 8, 6)
    nvg.fill_paint(vg, fadePaint)
    nvg.fill(vg)

    # Scroll bar
    shadowPaint = nvg.box_gradient(vg, x + w - 12 + 1, y + 4 + 1, 8, h - 8, 3, 4, nvg.rgba(0, 0, 0, 32), nvg.rgba(0, 0, 0, 92))
    nvg.begin_path(vg)
    nvg.rounded_rect(vg, x + w - 12, y + 4, 8, h - 8, 3)
    nvg.fill_paint(vg, shadowPaint)
    nvg.fill(vg)

    scrollh = (h / stackh) * (h - 8)
    shadowPaint = nvg.box_gradient(vg, x + w - 12 - 1, y + 4 + (h - 8 - scrollh) * u - 1, 8, scrollh, 3, 4, nvg.rgba(220, 220, 220, 255), nvg.rgba(128, 128, 128, 255))
    nvg.begin_path(vg)
    nvg.rounded_rect(vg, x + w - 12 + 1, y + 4 + 1 + (h - 8 - scrollh) * u, 8 - 2, scrollh - 2, 2)
    nvg.fill_paint(vg, shadowPaint)
    nvg.fill(vg)

    nvg.restore(vg)


def draw_colorwheel(vg: nvg.Context, x: float, y: float, w: float, h: float, t: float) -> None:
    hue = math.sin(t * 0.12)
    nvg.save(vg)

    cx = x + w * 0.5
    cy = y + h * 0.5
    w_or_h = w if w < h else h
    r1 = w_or_h * 0.5 - 5.0
    r0 = r1 - 20.0
    aeps = 0.5 / r1  # half a pixel arc length in radians (2pi cancels out).

    for i in range(6):
        a0 = i / 6.0 * math.pi * 2.0 - aeps
        a1 = (i + 1.0) / 6.0 * math.pi * 2.0 + aeps
        nvg.begin_path(vg)
        nvg.arc(vg, cx, cy, r0, a0, a1, nvg.Winding.cw.value)
        nvg.arc(vg, cx, cy, r1, a1, a0, nvg.Winding.ccw.value)
        nvg.close_path(vg)
        ax = cx + math.cos(a0) * (r0 + r1) * 0.5
        ay = cy + math.sin(a0) * (r0 + r1) * 0.5
        bx = cx + math.cos(a1) * (r0 + r1) * 0.5
        by = cy + math.sin(a1) * (r0 + r1) * 0.5
        paint = nvg.linear_gradient(vg, ax, ay, bx, by, nvg.hsla(a0 / (math.pi * 2), 1.0, 0.55, 255), nvg.hsla(a1 / (math.pi * 2), 1.0, 0.55, 255))
        nvg.fill_paint(vg, paint)
        nvg.fill(vg)

    nvg.begin_path(vg)
    nvg.circle(vg, cx, cy, r0 - 0.5)
    nvg.circle(vg, cx, cy, r1 + 0.5)
    nvg.stroke_color(vg, nvg.rgba(0, 0, 0, 64))
    nvg.stroke_width(vg, 1.0)
    nvg.stroke(vg)

    # Selector
    nvg.save(vg)
    nvg.translate(vg, cx, cy)
    nvg.rotate(vg, hue * math.pi * 2)

    # Marker on
    nvg.stroke_width(vg, 2.0)
    nvg.begin_path(vg)
    nvg.rect(vg, r0 - 1, -3, r1 - r0 + 2, 6)
    nvg.stroke_color(vg, nvg.rgba(255, 255, 255, 192))
    nvg.stroke(vg)

    paint = nvg.box_gradient(vg, r0 - 3, -5, r1 - r0 + 6, 10, 2, 4, nvg.rgba(0, 0, 0, 128), nvg.rgba(0, 0, 0, 0))
    nvg.begin_path(vg)
    nvg.rect(vg, r0 - 2 - 10, -4 - 10, r1 - r0 + 4 + 20, 8 + 20)
    nvg.rect(vg, r0 - 2, -4, r1 - r0 + 4, 8)
    nvg.path_winding(vg, nvg.Solidity.hole.value)
    nvg.fill_paint(vg, paint)
    nvg.fill(vg)

    # Center triangle
    r = r0 - 6
    ax = math.cos(120.0 / 180.0 * math.pi) * r
    ay = math.sin(120.0 / 180.0 * math.pi) * r
    bx = math.cos(-120.0 / 180.0 * math.pi) * r
    by = math.sin(-120.0 / 180.0 * math.pi) * r
    nvg.begin_path(vg)
    nvg.move_to(vg, r, 0)
    nvg.line_to(vg, ax, ay)
    nvg.line_to(vg, bx, by)
    nvg.close_path(vg)
    paint = nvg.linear_gradient(vg, r, 0, ax, ay, nvg.hsla(hue, 1.0, 0.5, 255), nvg.rgba(255, 255, 255, 255))
    nvg.fill_paint(vg, paint)
    nvg.fill(vg)
    paint = nvg.linear_gradient(vg, (r + ax) * 0.5, (0 + ay) * 0.5, bx, by, nvg.rgba(0, 0, 0, 0), nvg.rgba(0, 0, 0, 255))
    nvg.fill_paint(vg, paint)
    nvg.fill(vg)
    nvg.stroke_color(vg, nvg.rgba(0, 0, 0, 64))
    nvg.stroke(vg)

    # Select circle on triangle
    ax = math.cos(120.0 / 180.0 * math.pi) * r * 0.3
    ay = math.sin(120.0 / 180.0 * math.pi) * r * 0.4
    nvg.stroke_width(vg, 2.0)
    nvg.begin_path(vg)
    nvg.circle(vg, ax, ay, 5)
    nvg.stroke_color(vg, nvg.rgba(255, 255, 255, 192))
    nvg.stroke(vg)

    paint = nvg.radial_gradient(vg, ax, ay, 7, 9, nvg.rgba(0, 0, 0, 64), nvg.rgba(0, 0, 0, 0))
    nvg.begin_path(vg)
    nvg.rect(vg, ax - 20, ay - 20, 40, 40)
    nvg.circle(vg, ax, ay, 7)
    nvg.path_winding(vg, nvg.Solidity.hole.value)
    nvg.fill_paint(vg, paint)
    nvg.fill(vg)

    nvg.restore(vg)

    nvg.restore(vg)


def draw_lines(vg: nvg.Context, x: float, y: float, w: float, h: float, t: float) -> None:
    pad = 5.0
    s = w / 9.0 - pad * 2
    pts = [0.0] * 4 * 2
    fx = [0.0] * 4
    fy = [0.0] * 4
    joins = [nvg.LineCap.round.value, nvg.LineCap.round.value, nvg.LineCap.bevel.value, nvg.LineCap.miter.value]
    caps = [nvg.LineCap.butt.value, nvg.LineCap.round.value, nvg.LineCap.round.value, nvg.LineCap.round.value]

    nvg.save(vg)
    pts[0] = -s * 0.25 + math.cos(t * 0.3) * s * 0.5
    pts[1] = math.sin(t * 0.3) * s * 0.5
    pts[2] = -s * 0.25
    pts[3] = 0
    pts[4] = s * 0.25
    pts[5] = 0
    pts[6] = s * 0.25 + math.cos(-t * 0.3) * s * 0.5
    pts[7] = math.sin(-t * 0.3) * s * 0.5

    for i in range(4):
        for j in range(4):
            fx = x + s * 0.5 + (i * 9 + j) / 16.0 * w + pad
            fy = y - s * 0.5 + pad

            nvg.line_cap(vg, caps[i])
            nvg.line_join(vg, joins[j])

            nvg.stroke_width(vg, s * 0.3)
            nvg.stroke_color(vg, nvg.rgba(0, 0, 0, 160))
            nvg.begin_path(vg)
            nvg.move_to(vg, fx + pts[0], fy + pts[1])
            nvg.line_to(vg, fx + pts[2], fy + pts[3])
            nvg.line_to(vg, fx + pts[4], fy + pts[5])
            nvg.line_to(vg, fx + pts[6], fy + pts[7])
            nvg.stroke(vg)

            nvg.line_cap(vg, nvg.LineCap.butt.value)
            nvg.line_join(vg, nvg.LineCap.bevel.value)

            nvg.stroke_width(vg, 1.0)
            nvg.stroke_color(vg, nvg.rgba(0, 192, 255, 255))
            nvg.begin_path(vg)
            nvg.move_to(vg, fx + pts[0], fy + pts[1])
            nvg.line_to(vg, fx + pts[2], fy + pts[3])
            nvg.line_to(vg, fx + pts[4], fy + pts[5])
            nvg.line_to(vg, fx + pts[6], fy + pts[7])
            nvg.stroke(vg)

    nvg.restore(vg)


def load_demo_data(vg: nvg.Context, data: DemoData) -> int:
    for i in range(12):
        file = f"nanovg_demo_images/image{i+1}.jpg"
        file_asset_path = hello_imgui.asset_file_full_path(file)
        data.images[i] = nvg.create_image(vg, file_asset_path, 0)
        if data.images[i] == 0:
            print(f"Could not load {file}")
            return -1

    data.fontIcons = nvg.create_font(vg, "icons", hello_imgui.asset_file_full_path("fonts/entypo.ttf"))
    if data.fontIcons == -1:
        print("Could not add font icons.")
        return -1

    data.fontNormal = nvg.create_font(vg, "sans", hello_imgui.asset_file_full_path("fonts/Roboto/Roboto-Regular.ttf"))
    if data.fontNormal == -1:
        print("Could not add font italic.")
        return -1

    data.fontBold = nvg.create_font(vg, "sans-bold", hello_imgui.asset_file_full_path("fonts/Roboto/Roboto-Bold.ttf"))
    if data.fontBold == -1:
        print("Could not add font bold.")
        return -1

    data.fontEmoji = nvg.create_font(vg, "emoji", hello_imgui.asset_file_full_path("fonts/NotoEmoji-Regular.ttf"))
    if data.fontEmoji == -1:
        print("Could not add font emoji.")
        return -1

    nvg.add_fallback_font_id(vg, data.fontNormal, data.fontEmoji)
    nvg.add_fallback_font_id(vg, data.fontBold, data.fontEmoji)

    return 0


def free_demo_data(vg: nvg.Context, data: DemoData) -> None:
    for i in range(12):
        nvg.delete_image(vg, data.images[i])


def draw_paragraph(vg: nvg.Context, x: float, y: float, width: float, height: float, mx: float, my: float) -> None:
    lnum = 0
    gutter = 0
    gx = 0
    gy = 0
    text = "This is longer chunk of text.\n  \n  Would have used lorem ipsum but she    was busy jumping over the lazy dog with the fox and all the men who came to the aid of the party.🎉"
    hoverText = "Hover your mouse over the text to see calculated caret position."
    # boxText = "Testing\nsome multiline\ntext."

    nvg.save(vg)

    nvg.font_size(vg, 18.0)
    nvg.font_face(vg, "sans")
    nvg.text_align(vg, nvg.Align.align_left.value | nvg.Align.align_top.value)
    metrics = nvg.text_metrics(vg)
    lineh = metrics.lineh

    # The text break API can be used to fill a large buffer of rows,
    # or to iterate over the text just few lines (or just one) at a time.
    # The "next" variable of the last returned item tells where to continue.
    start = text

    # The rest is not ported, the demo manipulate too many C pointers
    text_rows = nvg.text_break_lines(vg, start, width)
    for i in range(len(text_rows)):
        row = text_rows[i]
        hit = mx > x and mx < (x + width) and my >= y and my < (y + lineh)

        nvg.begin_path(vg)
        nvg.fill_color(vg, nvg.rgba(255, 255, 255, 16))
        nvg.rect(vg, x, y, row.width, lineh)
        nvg.fill(vg)

        nvg.fill_color(vg, nvg.rgba(255, 255, 255, 255))
        nvg.text(vg, x, y, row.row_text)

        if hit:
            caretx = x if mx < x + row.width / 2 else x + row.width
            px = x
            glyphs = nvg.text_glyph_positions(vg, x, y, row.row_text)
            for j in range(len(glyphs)):
                x0 = glyphs[j].x
                x1 = glyphs[j + 1].x if j + 1 < len(glyphs) else x + row.width
                gx = x0 * 0.3 + x1 * 0.7
                if mx >= px and mx < gx:
                    caretx = glyphs[j].x
                px = gx

            nvg.begin_path(vg)
            nvg.fill_color(vg, nvg.rgba(255, 192, 0, 255))
            nvg.rect(vg, caretx, y, 1, lineh)
            nvg.fill(vg)

            gutter = lnum + 1
            gx = x - 10
            gy = y + lineh / 2

        lnum += 1
        y += lineh

        # Keep going
        #start = row.next

    if gutter:
        txt = str(gutter)
        nvg.font_size(vg, 12.0)
        nvg.text_align(vg, nvg.Align.align_right.value | nvg.Align.align_middle.value)

        bounds, _ = nvg.text_bounds(vg, gx, gy, txt)

        nvg.begin_path(vg)
        nvg.fill_color(vg, nvg.rgba(255, 192, 0, 255))
        nvg.rounded_rect(vg, math.floor(bounds[0]) - 4, math.floor(bounds[1]) - 2, math.floor(bounds[2] - bounds[0]) + 8, math.floor(bounds[3] - bounds[1]) + 4, (math.floor(bounds[3] - bounds[1]) + 4) / 2 - 1)
        nvg.fill(vg)

        nvg.fill_color(vg, nvg.rgba(32, 32, 32, 255))
        nvg.text(vg, gx, gy, txt)

    y += 20.0

    nvg.font_size(vg, 11.0)
    nvg.text_align(vg, nvg.Align.align_left.value | nvg.Align.align_top.value)
    nvg.text_line_height(vg, 1.2)

    bounds = nvg.text_box_bounds(vg, x, y, 150, hoverText)

    # Fade the tooltip out when close to it.
    gx = clamp(mx, bounds[0], bounds[2]) - mx
    gy = clamp(my, bounds[1], bounds[3]) - my
    a = math.sqrt(gx * gx + gy * gy) / 30.0
    a = clamp(a, 0, 1)
    nvg.global_alpha(vg, a)

    nvg.begin_path(vg)
    nvg.fill_color(vg, nvg.rgba(220, 220, 220, 255))
    nvg.rounded_rect(vg, bounds[0] - 2, bounds[1] - 2, math.floor(bounds[2] - bounds[0]) + 4, math.floor(bounds[3] - bounds[1]) + 4, 3)
    px = math.floor((bounds[2] + bounds[0]) / 2)
    nvg.move_to(vg, px, bounds[1] - 10)
    nvg.line_to(vg, px + 7, bounds[1] + 1)
    nvg.line_to(vg, px - 7, bounds[1] + 1)
    nvg.fill(vg)

    nvg.fill_color(vg, nvg.rgba(0, 0, 0, 220))
    nvg.text_box(vg, x, y, 150, hoverText)

    nvg.restore(vg)

def draw_widths(vg: nvg.Context, x: float, y: float, width: float) -> None:
    nvg.save(vg)

    nvg.stroke_color(vg, nvg.rgba(0, 0, 0, 255))

    for i in range(20):
        w = (i + 0.5) * 0.1
        nvg.stroke_width(vg, w)
        nvg.begin_path(vg)
        nvg.move_to(vg, x, y)
        nvg.line_to(vg, x + width, y + width * 0.3)
        nvg.stroke(vg)

    nvg.restore(vg)


def draw_caps(vg: nvg.Context, x: float, y: float, width: float) -> None:
    caps = [nvg.LineCap.butt.value, nvg.LineCap.round.value, nvg.LineCap.square.value]
    lineWidth = 8.0

    nvg.save(vg)

    nvg.begin_path(vg)
    nvg.rect(vg, x - lineWidth / 2, y, width + lineWidth, 40)
    nvg.fill_color(vg, nvg.rgba(255, 255, 255, 32))
    nvg.fill(vg)

    nvg.begin_path(vg)
    nvg.rect(vg, x, y, width, 40)
    nvg.fill_color(vg, nvg.rgba(255, 255, 255, 32))
    nvg.fill(vg)

    nvg.stroke_width(vg, lineWidth)
    for i in range(3):
        nvg.line_cap(vg, caps[i])
        nvg.stroke_color(vg, nvg.rgba(0, 0, 0, 255))
        nvg.begin_path(vg)
        nvg.move_to(vg, x, y + i * 10 + 5)
        nvg.line_to(vg, x + width, y + i * 10 + 5)
        nvg.stroke(vg)

    nvg.restore(vg)


def draw_scissor(vg: nvg.Context, x: float, y: float, t: float) -> None:
    nvg.save(vg)

    # Draw first rect and set scissor to it's area.
    nvg.translate(vg, x, y)
    nvg.rotate(vg, nvg.deg_to_rad(5))
    nvg.begin_path(vg)
    nvg.rect(vg, -20, -20, 60, 40)
    nvg.fill_color(vg, nvg.rgba(255, 0, 0, 255))
    nvg.fill(vg)
    nvg.scissor(vg, -20, -20, 60, 40)

    # Draw second rectangle with offset and rotation.
    nvg.translate(vg, 40, 0)
    nvg.rotate(vg, t)

    # Draw the intended second rectangle without any scissoring.
    nvg.begin_path(vg)
    nvg.rect(vg, -20, -10, 60, 30)
    nvg.fill_color(vg, nvg.rgba(255, 128, 0, 64))
    nvg.fill(vg)

    # Draw second rectangle with combined scissoring.
    nvg.begin_path(vg)
    nvg.rect(vg, -20, -10, 60, 30)
    nvg.fill_color(vg, nvg.rgba(255, 128, 0, 255))
    nvg.fill(vg)

    nvg.restore(vg)


def render_demo(vg: nvg.Context, mx: float, my: float, width: float, height: float, t: float, blowup: bool, data: DemoData) -> None:
    draw_eyes(vg, width - 250, 50, 150, 100, mx, my, t)
    draw_paragraph(vg, width - 450, 50, 150, 100, mx, my)
    draw_graph(vg, 0, height / 2, width, height / 2, t)
    draw_colorwheel(vg, width - 300, height - 300, 250.0, 250.0, t)

    # Line joints
    draw_lines(vg, 120, height - 50, 600, 50, t)

    # Line caps
    draw_widths(vg, 10, 50, 30)

    # Line caps
    draw_caps(vg, 10, 300, 30)

    draw_scissor(vg, 50, height - 80, t)

    nvg.save(vg)
    if blowup:
        nvg.rotate(vg, math.sin(t * 0.3) * 5.0 / 180.0 * math.pi)
        nvg.scale(vg, 2.0, 2.0)

    # Widgets
    draw_window(vg, "Widgets `n Stuff", 50, 50, 300, 400)
    x = 60
    y = 95
    draw_search_box(vg, "Search", x, y, 280, 25)
    y += 40
    draw_drop_down(vg, "Effects", x, y, 280, 28)
    popy = y + 14
    y += 45

    # Form
    draw_label(vg, "Login", x, y, 280, 20)
    y += 25
    draw_edit_box(vg, "Email", x, y, 280, 28)
    y += 35
    draw_edit_box(vg, "Password", x, y, 280, 28)
    y += 38
    draw_check_box(vg, "Remember me", x, y, 140, 28)
    draw_button(vg, ICON_LOGIN, "Sign in", x + 138, y, 140, 28, nvg.rgba(0, 96, 128, 255))
    y += 45

    # Slider
    draw_label(vg, "Diameter", x, y, 280, 20)
    y += 25
    draw_edit_box_num(vg, "123.00", "px", x + 180, y, 100, 28)
    draw_slider(vg, 0.4, x, y, 170, 28)
    y += 55

    draw_button(vg, ICON_TRASH, "Delete", x, y, 160, 28, nvg.rgba(128, 16, 8, 255))
    draw_button(vg, "", "Cancel", x + 170, y, 110, 28, nvg.rgba(0, 0, 0, 0))

    # Thumbnails box
    draw_thumbnails(vg, 365, popy - 30, 160, 300, data.images, 12, t)

    nvg.restore(vg)
