"""imgui_touch: the demo

A touch screen for Dear ImGui, as on a phone: the swipe, the long press, the pinch, the phone's keyboard. The Python
twin of imgui_touch_demo.cpp, section by section.
"""
###############################################################################
# imgui_touch_demo.py is a port of imgui_touch_demo.cpp (https://github.com/pthom/imgui_touch).
###############################################################################
import math

from imgui_bundle import ImVec2, hello_imgui, imgui, imgui_touch, immapp


def IMGUI_DEMO_MARKER(section: str) -> None:
    """Marker for the Explorer. Maps sections to source code."""
    pass


class _State:
    theme = -1  # -1: the application's
    taps = [0] * 8  # the taps of the sideways row's cards
    row_value = 0.5  # the sideways row's slider
    keyboard_line = ""
    keyboard_lines = "Several lines:\nmove the caret from the keyboard's space bar."
    keyboard_deep = ""
    canvas_zoom = 1.0
    canvas_offset = ImVec2(0.0, 0.0)  # where the canvas's content origin is, from its corner, in pixels
    # The gesture drawn on the canvas: its opacity (it fades once the fingers lift), one or two fingers, where
    gesture_alpha = 0.0
    gesture_two = False
    gesture_pos = ImVec2(0.0, 0.0)
    gesture_scale = 1.0
    gesture_kind = 0  # imgui_touch.PinchKind_


state = _State()


# =============================================================================
# Helpers
# =============================================================================
def help_marker(text: str) -> None:
    """A (?) that shows its text in a popup, opened by a click or a tap: a touch screen has no hover for a tooltip"""
    imgui.same_line()
    imgui.text_disabled("(?)")
    imgui.push_id(text)
    if imgui.is_item_clicked():
        imgui.open_popup("##help")
    if imgui.begin_popup("##help"):
        imgui.push_text_wrap_pos(imgui.get_font_size() * 25.0)
        imgui.text_unformatted(text)
        imgui.pop_text_wrap_pos()
        imgui.end_popup()
    imgui.pop_id()


def setting_row(label: str) -> None:
    """A label on the left of a settings table's row; the widgets go in the second column"""
    imgui.table_next_row()
    imgui.table_next_column()
    imgui.align_text_to_frame_padding()
    imgui.text_unformatted(label)
    imgui.table_next_column()


def has_touch_layer() -> bool:
    """Without the touch layer (an app that shows this demo without imgui_touch.setup()), a note instead of the
    section"""
    if imgui_touch.is_installed():
        return True
    imgui.text_wrapped("This application did not set up the touch layer: imgui_touch.setup(), once after "
                       "imgui.create_context() (Hello ImGui does it).")
    return False


# =============================================================================
# Gestures
# =============================================================================
def zoomable_canvas(str_id: str, size: ImVec2) -> None:
    """A canvas that zooms and pans, as a map or an image viewer does. With a mouse: the wheel zooms (it claims the
    wheel while hovered: imgui.set_item_key_owner), a drag pans. With fingers: one finger pans at once
    (imgui_touch.set_item_takes_drags), two fingers zoom and pan at once (imgui_touch.item_pinch: the gesture's
    data)."""
    io = imgui.get_io()
    p0 = imgui.get_cursor_screen_pos()
    p1 = ImVec2(p0.x + size.x, p0.y + size.y)

    def zoom_around(point: ImVec2, factor: float) -> None:
        """Zoom by `factor` around a point of the screen: the content under it stays there."""
        new_zoom = min(max(state.canvas_zoom * factor, 0.25), 8.0)
        px, py = point.x - p0.x, point.y - p0.y
        state.canvas_offset = ImVec2(px - (px - state.canvas_offset.x) * new_zoom / state.canvas_zoom,
                                     py - (py - state.canvas_offset.y) * new_zoom / state.canvas_zoom)
        state.canvas_zoom = new_zoom

    imgui.invisible_button(str_id, size)
    imgui_touch.set_item_takes_drags()
    pinch = imgui_touch.item_pinch()
    if pinch.active:
        zoom_around(pinch.center, pinch.scale_delta)
        state.canvas_offset = ImVec2(state.canvas_offset.x + pinch.center_delta.x,
                                     state.canvas_offset.y + pinch.center_delta.y)
    elif imgui.is_item_active():
        state.canvas_offset = ImVec2(state.canvas_offset.x + io.mouse_delta.x, state.canvas_offset.y + io.mouse_delta.y)
    if imgui.set_item_key_owner(imgui.Key.mouse_wheel_y) and io.mouse_wheel != 0.0:
        zoom_around(io.mouse_pos, 1.1**io.mouse_wheel)

    # The gesture, as the canvas sees it: a dot under one finger (or the mouse); for two fingers, a ring at their
    # middle that follows their spread, and the layer's decision (pinch or pan). It fades once they lift.
    if pinch.active:
        state.gesture_two, state.gesture_pos = True, pinch.center
        state.gesture_scale, state.gesture_kind = pinch.scale, pinch.kind
        state.gesture_alpha = 1.0
    elif imgui.is_item_active():
        state.gesture_two, state.gesture_pos = False, io.mouse_pos
        state.gesture_alpha = 1.0
    elif state.gesture_alpha > 0.0:
        state.gesture_alpha = max(0.0, state.gesture_alpha - io.delta_time * 3.0)
        hello_imgui.request_refresh()  # an app that idles still draws the fade

    draw_list = imgui.get_window_draw_list()
    rounding = imgui.get_style().frame_rounding
    em = imgui.get_font_size()
    draw_list.add_rect_filled(p0, p1, imgui.get_color_u32(imgui.Col_.frame_bg), rounding)
    draw_list.push_clip_rect(p0, p1, True)
    step = em * state.canvas_zoom  # a grid of 1 em at zoom 1
    grid_color = imgui.get_color_u32(imgui.Col_.border)
    x = p0.x + math.fmod(state.canvas_offset.x, step)
    while x < p1.x:
        draw_list.add_line(ImVec2(x, p0.y), ImVec2(x, p1.y), grid_color)
        x += step
    y = p0.y + math.fmod(state.canvas_offset.y, step)
    while y < p1.y:
        draw_list.add_line(ImVec2(p0.x, y), ImVec2(p1.x, y), grid_color)
        y += step
    center = ImVec2(p0.x + state.canvas_offset.x + 4.0 * step, p0.y + state.canvas_offset.y + 3.0 * step)
    draw_list.add_circle_filled(center, 1.5 * step, imgui.get_color_u32(imgui.Col_.slider_grab_active))
    draw_list.add_rect_filled(ImVec2(center.x + 3.0 * step, center.y - step),
                              ImVec2(center.x + 6.0 * step, center.y + step),
                              imgui.get_color_u32(imgui.Col_.button_active))
    if state.gesture_alpha > 0.0:
        color = imgui.get_color_u32(imgui.Col_.text, state.gesture_alpha)
        pos = state.gesture_pos
        if not state.gesture_two:
            draw_list.add_circle_filled(pos, 0.4 * em, color)
        else:
            radius = 1.5 * em * state.gesture_scale
            draw_list.add_circle(pos, radius, color, 0, 2.0)
            draw_list.add_circle_filled(pos, 0.15 * em, color)
            kind = ("pinch" if state.gesture_kind == imgui_touch.PinchKind_.pinch
                    else "pan" if state.gesture_kind == imgui_touch.PinchKind_.pan else "two fingers")
            draw_list.add_text(ImVec2(pos.x + radius + 0.3 * em, pos.y - 0.5 * em), color, kind)
    draw_list.pop_clip_rect()
    draw_list.add_rect(p0, p1, imgui.get_color_u32(imgui.Col_.border), rounding)
    draw_list.add_text(ImVec2(p0.x + imgui.get_style().frame_padding.x, p1.y - imgui.get_text_line_height_with_spacing()),
                       imgui.get_color_u32(imgui.Col_.text), f"zoom x{state.canvas_zoom:.2f}")


# The text to select in the touch zone (read-only)
SELECTABLE_TEXT = ("Napoleon's army crossed the Niemen in June 1812, with more than four hundred thousand men. "
                   "Six months later, fewer than ten thousand came back.")


TOUCH_SETUP_CODE = """imgui.create_context()
imgui_touch.setup()            # the touch layer: swipe, long press, pinch

# The render loop: nothing to add, the layer runs inside imgui.new_frame() and imgui.render().
# - An app that sleeps when idle keeps drawing while imgui_touch.is_animating().
# - A widget that a finger drags: imgui_touch.set_item_takes_drags() right after it.
# - A widget that zooms: imgui_touch.item_pinch() right after it (set_item_pinch_as_wheel() if it zooms by the wheel).
# Hello ImGui does the setup itself (RunnerParams.touch_config)."""


def demo_gestures() -> None:
    """The settings change the application's touch layer, live. "Simulate touch" lets the mouse play a finger."""
    IMGUI_DEMO_MARKER("Gestures")
    imgui.set_next_item_open(True, imgui.Cond_.first_use_ever)
    if not imgui.collapsing_header("Gestures"):
        return
    if not has_touch_layer():
        return
    io = imgui.get_io()
    em = imgui.get_font_size()
    imgui.text_wrapped("The gestures of a phone: a finger drags the content (with inertia, and a bounce at the end), "
                       "a long press is a right click, two fingers pinch the font.")
    if imgui.tree_node("The setup code"):
        imgui.text_unformatted(TOUCH_SETUP_CODE)
        imgui.tree_pop()

    config = imgui_touch.get_config()
    if imgui.begin_table("##touch_settings", 2, imgui.TableFlags_.sizing_fixed_fit):
        if not (io.config_flags & imgui.ConfigFlags_.is_touch_screen):
            setting_row("On a desktop")
            _, config.simulate_touch = imgui.checkbox("Simulate touch", config.simulate_touch)
            help_marker("The mouse plays a finger (imgui_touch.Config.simulate_touch): every gesture works in the zone "
                        "below, as on a phone.\n\n"
                        "- Drag up or down to scroll the content. Start moving as soon as you press, as with a "
                        "finger.\n"
                        "- Press and hold, then release: a long press, which opens the zone's context menu (a right "
                        "click).")
        setting_row("Swipe")
        scroll_modes = ["Touch", "Always", "Off"]  # the order of imgui_touch.ScrollMode_
        imgui.set_next_item_width(8.0 * em)
        _, config.scroll_mode = imgui.combo("##scroll_mode", config.scroll_mode, scroll_modes)
        help_marker("Touch: the swipe follows a finger only. Always: the mouse's left button drags the content too, "
                    "while the mouse stays a mouse.")
        setting_row("Pinch")
        _, config.pinch_scales_font = imgui.checkbox("scales the font", config.pinch_scales_font)
        setting_row("Hold")
        imgui.set_next_item_width(8.0 * em)
        _, config.hold_seconds = imgui.slider_float("##hold", config.hold_seconds, 0.0, 1.0, "%.2f s")
        help_marker("A finger still for this long hands its press to the widget under it, which then gets the drag (a "
                    "slider, a text selection). At zero, the widgets get every press at once.")
        setting_row("Long press")
        _, config.long_press_is_right_click = imgui.checkbox("is a right click", config.long_press_is_right_click)
        setting_row("Its delay")
        imgui.set_next_item_width(8.0 * em)
        _, config.long_press_seconds = imgui.slider_float("##long_press", config.long_press_seconds, 0.3, 2.0, "%.2f s")
        setting_row("Scroll bars")
        _, config.thin_scrollbars = imgui.checkbox("thin", config.thin_scrollbars)
        imgui.end_table()

    imgui.begin_child("##touch_zone", ImVec2(0.0, 16.0 * em), imgui.ChildFlags_.borders)
    imgui.bullet()
    imgui.text_wrapped("Swipe: a finger that drags this zone scrolls it, with inertia, and a bounce at the end.")
    imgui.bullet()
    imgui.text_wrapped("Tap: a click, when the finger lifts.")
    imgui.bullet()
    imgui.text_wrapped("Hold, then drag: the widget under the finger takes it (the text below: it selects).")
    imgui.bullet()
    imgui.text_wrapped("Long press, then lift: a right click (this zone's context menu).")
    imgui.bullet()
    imgui.text_wrapped("Two fingers: a pinch scales the font (on the canvas, it zooms the canvas); moved together, a "
                       "right drag.")
    # A text to select: a drag that starts on it scrolls the zone; a short hold, then a drag, selects (as on a
    # phone). A ring shows when the hold took effect.
    imgui.text_wrapped("Select a few words: a short hold, then a drag.")
    imgui.input_text_multiline("##select", SELECTABLE_TEXT, ImVec2(-imgui.FLT_MIN, 4.0 * em),
                               imgui.InputTextFlags_.read_only | imgui.InputTextFlags_.word_wrap)

    zoomable_canvas("##canvas", ImVec2(16.0 * em, 8.0 * em))
    help_marker("A canvas that zooms and pans, as a plot or an image viewer does:\n\n"
                "- It calls imgui_touch.set_item_takes_drags() right after it: a drag that starts on it pans it at "
                "once. So the zone cannot be scrolled from inside the canvas.\n"
                "- It claims the wheel while hovered: if imgui.set_item_key_owner(imgui.Key.mouse_wheel_y).\n"
                "- It reads two fingers' gesture with imgui_touch.item_pinch(): their spread zooms it and their move "
                "pans it, both at once, as on a map. The font keeps its size.")
    if imgui.begin_popup_context_window("##zone_menu"):
        imgui.text_unformatted("The zone's context menu: a right click, or a long press")
        imgui.end_popup()

    # A child that scrolls sideways: a swipe inside scrolls it, not the zone. Its buttons count their taps. Its slider
    # takes the sideways drags (imgui_touch.set_item_takes_drags(imgui_touch.Axis_.x)): a sideways drag on it moves it
    # at once
    imgui.text_wrapped("A sideways swipe scrolls this row; a tap clicks a button; a sideways drag moves the slider:")
    imgui.begin_child("##sideways", ImVec2(0.0, 5.0 * em), imgui.ChildFlags_.borders,
                      imgui.WindowFlags_.horizontal_scrollbar)
    card_width = max(6.0 * em, imgui.get_content_region_avail().x * 0.3)  # three per screen: the row scrolls
    imgui.set_next_item_width(card_width)
    _, state.row_value = imgui.slider_float("##row_slider", state.row_value, 0.0, 1.0)
    imgui_touch.set_item_takes_drags(imgui_touch.Axis_.x)
    for i in range(len(state.taps)):
        imgui.same_line()
        if imgui.button(f"Card {i + 1}\n{state.taps[i]} taps###card{i}", ImVec2(card_width, 3.0 * em)):
            state.taps[i] += 1
    imgui.end_child()
    for i in range(1, 9):
        imgui.text(f"More content, to scroll ({i})")
    imgui.end_child()
    # is_animating(): an application that sleeps when nothing happens keeps drawing frames meanwhile
    imgui.text(f"Moving on its own: {'yes' if imgui_touch.is_animating() else 'no'}")


# =============================================================================
# Keyboard
# =============================================================================
def demo_keyboard() -> None:
    """The phone's keyboard, in a browser: the fields of all kinds, one of them in a child that scrolls."""
    IMGUI_DEMO_MARKER("Keyboard")
    if not imgui.collapsing_header("Keyboard"):
        return
    if not has_touch_layer():
        return
    em = imgui.get_font_size()
    imgui.text_wrapped("In a browser on a phone: tap a field, then the keyboard button that shows next to it (or the "
                       "field again). The phone's keyboard opens, and a full-screen window keeps out of it "
                       "(imgui_touch.get_keyboard_insets()). Hello ImGui sets it up (in C++: "
                       "ImGuiTouch::SetupEmscriptenKeyboard()).")
    _, state.keyboard_line = imgui.input_text_with_hint("text", "type here", state.keyboard_line)
    _, state.keyboard_lines = imgui.input_text_multiline("lines", state.keyboard_lines, ImVec2(0.0, 5.0 * em))

    imgui.text_wrapped("A field in a child that scrolls: it stays above the keyboard.")
    imgui.begin_child("##keyboard_child", ImVec2(0.0, 10.0 * em), imgui.ChildFlags_.borders)
    for i in range(1, 13):
        imgui.text(f"Content above the field ({i})")
    _, state.keyboard_deep = imgui.input_text_with_hint("field", "type here", state.keyboard_deep)
    for i in range(1, 13):
        imgui.text(f"Content below the field ({i})")
    imgui.end_child()


# =============================================================================
# Demo window
# =============================================================================
def show_demo_contents() -> None:
    imgui.text_wrapped("ImGuiTouch: a touch screen for Dear ImGui, as on a phone")
    # The theme applies to the whole application: a check of both themes on a phone
    imgui.align_text_to_frame_padding()
    imgui.text_unformatted("Theme")
    imgui.same_line()
    clicked, state.theme = imgui.radio_button("Dark", state.theme, 0)
    if clicked:
        imgui.style_colors_dark()
    imgui.same_line()
    clicked, state.theme = imgui.radio_button("Light", state.theme, 1)
    if clicked:
        imgui.style_colors_light()
    imgui.separator()
    demo_gestures()
    demo_keyboard()


def gui() -> None:
    show_demo_contents()


def main() -> None:
    immapp.run(gui, window_title="imgui_touch demo", window_size=(600, 750))


if __name__ == "__main__":
    main()
