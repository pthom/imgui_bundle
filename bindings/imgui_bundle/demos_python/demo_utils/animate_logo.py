"""A logo that appears at the center of the screen, then flies to the top right corner of the page it decorates"""
import webbrowser
from imgui_bundle import imgui, hello_imgui, immapp, ImVec4, ImVec2

APPEAR, HOLD, FLIGHT = 0.3, 0.4, 0.6  # s: the logo fades in at the center, stays, then flies to its corner

Rect = tuple[ImVec2, ImVec2]  # min, max


def _ease_out_cubic(t: float) -> float:
    return 1.0 - (1.0 - t) ** 3


def _ease_in_out_cubic(t: float) -> float:
    return 4.0 * t ** 3 if t < 0.5 else 1.0 - (2.0 - 2.0 * t) ** 3 / 2.0


def _lerp_rect(a: Rect, b: Rect, k: float) -> Rect:
    return (ImVec2(a[0].x + (b[0].x - a[0].x) * k, a[0].y + (b[0].y - a[0].y) * k),
            ImVec2(a[1].x + (b[1].x - a[1].x) * k, a[1].y + (b[1].y - a[1].y) * k))


def _centered_rect(center: ImVec2, width: float, height: float) -> Rect:
    return (ImVec2(center.x - width / 2, center.y - height / 2), ImVec2(center.x + width / 2, center.y + height / 2))


@immapp.static(start_time=-1.0)
def animate_logo(logo_file: str, ratio_width_height: float, final_alpha: float, url: str) -> None:
    """The logo appears at the center of the screen, then flies to the top right corner of the area that remains in
    the window: call it before the content it decorates. It plays once, then stays there as a link to url."""
    static = animate_logo
    if static.start_time < 0:
        static.start_time = immapp.clock_seconds()
    t = immapp.clock_seconds() - static.start_time
    if hello_imgui.prefers_reduced_motion():  # no flight: the logo is in its corner at once
        t = APPEAR + HOLD + FLIGHT

    # Where it lands: the top right corner of the area that remains, smaller on a narrow screen
    em = imgui.get_font_size()
    pos, avail = imgui.get_cursor_screen_pos(), imgui.get_content_region_avail()
    height = em * (2.5 if avail.x > em * 40 else 1.8)
    right = pos.x + avail.x
    corner: Rect = (ImVec2(right - height * ratio_width_height, pos.y), ImVec2(right, pos.y + height))

    # Where it appears: big, at the center of the screen
    viewport = imgui.get_main_viewport()
    big_height = min(viewport.size.x / ratio_width_height, viewport.size.y) * 0.5
    center = _centered_rect(viewport.get_center(), big_height * ratio_width_height, big_height)

    if t < APPEAR:  # it fades in, growing a little
        k = _ease_out_cubic(t / APPEAR)
        smaller = _centered_rect(viewport.get_center(), big_height * ratio_width_height * 0.9, big_height * 0.9)
        rect, alpha = _lerp_rect(smaller, center, k), k
    elif t < APPEAR + HOLD:
        rect, alpha = center, 1.0
    else:  # it flies to its corner, and fades to final_alpha
        k = _ease_in_out_cubic(min((t - APPEAR - HOLD) / FLIGHT, 1.0))
        rect, alpha = _lerp_rect(center, corner, k), 1.0 + (final_alpha - 1.0) * k
    if t < APPEAR + HOLD + FLIGHT:
        hello_imgui.request_refresh()  # it moves on its own (a drawing, not a widget)

    mouse = imgui.get_mouse_pos()
    if rect[0].x <= mouse.x <= rect[1].x and rect[0].y <= mouse.y <= rect[1].y:
        alpha = 1.0
        if imgui.is_mouse_clicked(0):
            webbrowser.open(url)

    # Over the page's widgets, but clipped to the page: it never covers what surrounds it (the explorer's header)
    texture = imgui.ImTextureRef(hello_imgui.im_texture_id_from_asset(logo_file))
    window_pos, window_size = imgui.get_window_pos(), imgui.get_window_size()
    draw_list = imgui.get_foreground_draw_list()
    draw_list.push_clip_rect(window_pos, ImVec2(window_pos.x + window_size.x, window_pos.y + window_size.y))
    draw_list.add_image(texture, rect[0], rect[1], ImVec2(0, 0), ImVec2(1, 1),
                        imgui.get_color_u32(ImVec4(1.0, 1.0, 1.0, alpha)))
    draw_list.pop_clip_rect()
