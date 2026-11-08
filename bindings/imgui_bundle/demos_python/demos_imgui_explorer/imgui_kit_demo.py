"""imgui_kit: the demo

Small, standalone additions to Dear ImGui: em units, a row that fills its line, aligned groups, columns, a label
column, a flow, a help marker, icon buttons, a segmented switch. The Python twin of imgui_kit_demo.cpp, section by
section.
"""
###############################################################################
# imgui_kit_demo.py is a port of imgui_kit_demo.cpp (https://github.com/pthom/imgui_kit). In Python, the
# Begin/End pairs are also context managers: `with imgui_kit.fill_row("slice") as row: ... row.tail() ...`.
###############################################################################
import math
from typing import List

from imgui_bundle import ImVec2, imgui, imgui_kit, immapp


def IMGUI_DEMO_MARKER(section: str) -> None:
    """Marker for the Explorer. Maps sections to source code."""
    pass


class _State:
    font_size = 0.0  # 0: the application's size, read at the first frame
    app_colors: List[imgui.ImVec4] = []
    app_rounding = -1.0  # -1: not read yet
    theme = 0
    slice = 37
    text = "An InputText fills the line too"
    preset = 0
    zoom = 1.0
    view = 0
    unit = 1
    period = 1
    eq = [0.3, 0.6, 0.45]
    labels_align = 0
    volume = 0.5
    balance = 0.0
    fit_width_em = 16.0
    fit_lines = 2
    gamma = 1.0
    flip = False
    resizable_text = "A text field that the reader can make larger.\nDrag its corner."
    text_size = ImVec2(0, 0)  # set at the first frame, in em (the font must exist)
    child_size = ImVec2(0, 0)
    muted = False
    touch_value = 0.5
    taps = [0] * 8  # the taps of the sideways row's cards
    row_value = 0.5  # the sideways row's slider
    keyboard_line = ""
    keyboard_lines = "Several lines:\nmove the caret from the keyboard's space bar."
    keyboard_deep = ""
    canvas_zoom = 1.0
    canvas_offset = ImVec2(0.0, 0.0)  # where the canvas's content origin is, from its corner, in pixels


state = _State()


# =============================================================================
# Toolbar: theme, font size, frame rounding
# =============================================================================
def next_line_if_too_wide(widget_width: float) -> None:
    """After a label, a widget too wide for the rest of the line goes under it: a narrow window (a phone) keeps its
    rows on screen"""
    if widget_width > imgui.get_content_region_avail().x:
        imgui.new_line()


def demo_toolbar() -> None:
    """The theme and the frame rounding apply to the whole application; "App" restores the colors it had.
    The font size applies to the demo."""
    IMGUI_DEMO_MARKER("Toolbar")
    style = imgui.get_style()
    if state.app_rounding < 0.0:
        for i in range(imgui.Col_.count.value):
            c = style.color_(i)
            state.app_colors.append(imgui.ImVec4(c.x, c.y, c.z, c.w))
        state.app_rounding = style.frame_rounding

    # Each row: a label, then its widgets, aligned at the widest label
    with imgui_kit.label_column("toolbar"):
        imgui_kit.label("Theme")
        themes = ["App", "Dark", "Light", "Classic"]
        next_line_if_too_wide(imgui_kit.segmented_switch_width(themes))
        changed, state.theme = imgui_kit.segmented_switch("##theme", state.theme, themes)
        if changed:
            if state.theme == 0:
                for i, c in enumerate(state.app_colors):
                    style.set_color_(i, c)
            elif state.theme == 1:
                imgui.style_colors_dark()
            elif state.theme == 2:
                imgui.style_colors_light()
            else:
                imgui.style_colors_classic()

        # The sliders fill their rows (fill rows): the rows fit a phone's width
        imgui_kit.label("Font size")
        with imgui_kit.fill_row("font_size"):
            _, state.font_size = imgui.slider_float("##font_size", state.font_size, 8.0, 40.0, "%.0f px")

        imgui_kit.label("Frame rounding")
        with imgui_kit.fill_row("rounding") as row:
            _, style.frame_rounding = imgui.slider_float("##rounding", style.frame_rounding, 0.0, 12.0, "%.0f px")
            row.tail()
            imgui_kit.help_marker("The style's frame_rounding: imgui.get_style().frame_rounding. Buttons, sliders, "
                                  "input fields and the segmented switch round their corners with it. 0 gives square "
                                  "frames; half the frame's height gives a pill.")
            imgui.same_line()
            if imgui.button("Reset"):  # the application's font size and frame rounding
                state.font_size = style.font_size_base
                style.frame_rounding = state.app_rounding

# =============================================================================
# Em units
# =============================================================================
def demo_em_units() -> None:
    IMGUI_DEMO_MARKER("Em units")
    if not imgui.collapsing_header("Em units"):
        return
    imgui.text_wrapped("Sizes in em follow the font: the first button is 8 em wide and 2 em high, on any screen. "
                       "Change the font size at the top: it grows with the text, as a standard button does. "
                       "The last button keeps its size in pixels: at a large font, its label gets cut.")
    imgui.button("8 x 2 em", imgui_kit.em_to_vec2(8, 2))
    imgui.same_line()
    imgui.button("A standard button")
    imgui.same_line()
    imgui.button("100 x 30 px", (100, 30))
    imgui.same_line()
    imgui_kit.help_marker("em_to_vec2(8, 2) gives the size in pixels, from the current font size.")
    imgui.text(f"1 em = {imgui_kit.em_size():.1f} px")


# =============================================================================
# Layout
# =============================================================================
def demo_fill_row() -> None:
    IMGUI_DEMO_MARKER("Layout/Fill row")
    if not imgui.tree_node("Fill row"):
        return
    imgui.text_wrapped("The slider fills the line; the arrows and the (i) stay on the right. Resize the window.")
    with imgui_kit.fill_row("slice") as row:
        _, state.slice = imgui.slider_int("##slice", state.slice, 0, 59, "Slice %d of 59")
        row.tail()
        if imgui.arrow_button("##prev", imgui.Dir.left) and state.slice > 0:
            state.slice -= 1
        imgui.same_line()
        if imgui.arrow_button("##next", imgui.Dir.right) and state.slice < 59:
            state.slice += 1
        imgui.same_line()
        imgui_kit.help_marker("fill_row(), the slider, row.tail(), the arrows and this marker.")

    with imgui_kit.fill_row("input") as row:
        _, state.text = imgui.input_text("##input", state.text)
        row.tail()
        imgui.button("Send")
    imgui.tree_pop()


def demo_aligned_group() -> None:
    IMGUI_DEMO_MARKER("Layout/Aligned group")
    if not imgui.tree_node("Aligned group"):
        return
    with imgui_kit.aligned_group("right", 1.0):
        imgui.button("Cancel")
        imgui.same_line()
        imgui.button("Apply")

    with imgui_kit.aligned_group("center", 0.5):
        imgui.text("A centered group")

    with imgui_kit.aligned_group("center_two_lines", 0.5):
        imgui.text("Two lines, centered as one box:")
        imgui.button("OK")
    imgui.same_line()
    imgui_kit.help_marker("The group's box is centered, not each line: the button stays at the box's left.")
    imgui.tree_pop()


def demo_column() -> None:
    IMGUI_DEMO_MARKER("Layout/Column")
    if not imgui.tree_node("Column"):
        return
    imgui.text_wrapped("Each column knows its width: the aligned groups inside it center its slider and its help "
                       "under its label, whatever the label's length.")
    labels = ["Bass", "Midrange", "Treble"]
    helps = ["Bass: below 250 Hz.", "Midrange: from 250 Hz to 4 kHz.", "Treble: above 4 kHz."]
    for i in range(3):
        imgui.push_id(i)
        with imgui_kit.column("column"):
            imgui.text(labels[i])
            with imgui_kit.aligned_group("slider", 0.5):
                _, state.eq[i] = imgui.v_slider_float("##v", imgui_kit.em_to_vec2(1.6, 6), state.eq[i], 0.0, 1.0, "")
            with imgui_kit.aligned_group("help", 0.5):
                imgui_kit.help_marker(helps[i])
        imgui.pop_id()
        imgui.same_line(0.0, imgui_kit.em_size(1.5))
    imgui.new_line()
    imgui.tree_pop()


def demo_label_column() -> None:
    IMGUI_DEMO_MARKER("Layout/Label column")
    if not imgui.tree_node("Label column"):
        return
    imgui.text_wrapped("Labels on the left, and the widgets after them aligned at the widest label. "
                       "After its label, a row is a normal line: same_line() adds widgets to it.")
    with imgui_kit.label_column("audio", 0.0 if state.labels_align == 0 else 1.0):
        imgui_kit.label("Labels")
        _, state.labels_align = imgui_kit.segmented_switch("##labels_align", state.labels_align, ["Left", "Right"])
        imgui_kit.label("Volume")
        _, state.volume = imgui.slider_float("##volume", state.volume, 0.0, 1.0)
        imgui_kit.label("Left/right balance")
        _, state.balance = imgui.slider_float("##balance", state.balance, -1.0, 1.0)
        imgui_kit.label("Output")
        _, state.muted = imgui.checkbox("Muted", state.muted)
        imgui.same_line()
        imgui.button("Test sound")
    imgui.tree_pop()


def demo_group_panel() -> None:
    IMGUI_DEMO_MARKER("Layout/Group panel")
    if not imgui.tree_node("Group panel"):
        return
    imgui.text_wrapped("A group in a frame, its label in the frame's top border. The look of thedmd's group panel "
                       "(Dear ImGui issue #1496).")
    with imgui_kit.group_panel("Image info"):
        imgui.text("Size: 640 x 480")
        imgui.text("Channels: 3")
        imgui.text("Depth: 8 bits")
    imgui.same_line()
    with imgui_kit.group_panel("Display"):
        with imgui_kit.label_column("display"):
            imgui_kit.label("Gamma")
            imgui.set_next_item_width(imgui_kit.em_size(8))
            _, state.gamma = imgui.slider_float("##gamma", state.gamma, 0.2, 3.0)
            imgui_kit.label("Flip")
            _, state.flip = imgui.checkbox("##flip", state.flip)
    imgui.tree_pop()


def demo_flow() -> None:
    IMGUI_DEMO_MARKER("Layout/Flow")
    if not imgui.tree_node("Flow"):
        return
    imgui.text_wrapped("The buttons stay on a line while they fit. Resize the window: they flow to the next line.")
    presets = ["Coral", "Lavender", "Mint", "Sunflower yellow", "Sky", "Peach", "Forest green",
               "Sand", "Honey", "Midnight blue", "Rose", "Turquoise", "Olive", "Salmon",
               "Steel blue", "Plum", "Ivory", "Terracotta", "Sea green", "Mustard", "Slate gray",
               "Cherry red", "Teal", "Custom"]  # enough to flow onto several lines in a wide window
    with imgui_kit.flow("presets"):
        for i, preset in enumerate(presets):
            imgui_kit.flow_next()
            selected = i == state.preset
            if selected:
                imgui.push_style_color(imgui.Col_.button, imgui.get_style_color_vec4(imgui.Col_.button_active))
            if imgui.button(preset):
                state.preset = i
            if selected:
                imgui.pop_style_color()
    imgui.tree_pop()


def demo_layout() -> None:
    IMGUI_DEMO_MARKER("Layout")
    if not imgui.collapsing_header("Layout"):
        return
    imgui.text_wrapped("These helpers measure their parts on the previous frame. The first frame draws them hidden.")
    demo_fill_row()
    demo_aligned_group()
    demo_column()
    demo_label_column()
    demo_group_panel()
    demo_flow()


# =============================================================================
# Widgets
# =============================================================================
def demo_help_marker() -> None:
    IMGUI_DEMO_MARKER("Widgets/Help marker")
    if not imgui.tree_node("Help marker"):
        return
    imgui.text_wrapped("A touch screen has no hover: a tooltip never shows there. The (i) opens on a tap as well, "
                       "so its text reaches every user.")
    imgui.bullet_text("With a mouse: hover to read, click to pin.")
    imgui.bullet_text("On a touch screen: tap to open, tap elsewhere to close.")
    imgui.text("Try it:")
    imgui.same_line()
    imgui_kit.help_marker("With a mouse, hovering shows this text, and a click pins it until a click elsewhere. "
                          "On a touch screen, a tap opens it.")
    imgui.text("Any content, with help_marker_ctx():")
    imgui.same_line()
    with imgui_kit.help_marker_ctx("##custom") as shown:
        if shown:
            imgui.text("A help with widgets:")
            imgui.bullet_text("a list")
            imgui.button("and a button")
    imgui.tree_pop()


def demo_icon_button() -> None:
    IMGUI_DEMO_MARKER("Widgets/Icon button")
    if not imgui.tree_node("Icon button"):
        return
    imgui.text_wrapped("The icons are drawn with the window's draw list (lines, rectangles, circles): "
                       "no icon font to load, and they follow the font size.")
    Icon = imgui_kit.Icon_
    if imgui_kit.icon_button("##minus", Icon.minus):
        state.zoom /= 1.25
    imgui.same_line()
    if imgui_kit.icon_button("##plus", Icon.plus):
        state.zoom *= 1.25
    imgui.same_line()
    if imgui_kit.icon_button("##zoom_in", Icon.zoom_in):
        state.zoom *= 1.25
    imgui.same_line()
    if imgui_kit.icon_button("##zoom_out", Icon.zoom_out):
        state.zoom /= 1.25
    imgui.same_line()
    if imgui_kit.icon_button("##zoom_1", Icon.zoom_one_to_one):
        state.zoom = 1.0
    imgui.same_line()
    if imgui_kit.icon_button("##zoom_fit", Icon.zoom_fit):
        state.zoom = 0.5
    imgui.same_line()
    imgui.text(f"zoom: {state.zoom:.2f}")
    imgui.tree_pop()


def demo_segmented_switch() -> None:
    IMGUI_DEMO_MARKER("Widgets/Segmented switch")
    if not imgui.tree_node("Segmented switch"):
        return
    imgui.text_wrapped("Its corners follow the style's frame_rounding, as a button's do: change it at the top.")
    views = ["Demo", "Code"]
    _, state.view = imgui_kit.segmented_switch("##view", state.view, views)
    imgui.same_line()
    imgui.text(f"showing: {views[state.view]}")
    _, state.unit = imgui_kit.segmented_switch("##unit", state.unit, ["mm", "cm", "inch"])

    imgui.text_wrapped("One switch as a pill: push a frame_rounding of half the frame's height around it.")
    imgui.push_style_var(imgui.StyleVar_.frame_rounding, imgui.get_frame_height() * 0.5)
    _, state.period = imgui_kit.segmented_switch("##period", state.period, ["Day", "Week", "Month"])
    imgui.pop_style_var()
    imgui.tree_pop()


def demo_fit_text() -> None:
    IMGUI_DEMO_MARKER("Widgets/Fit text")
    if not imgui.tree_node("Fit text"):
        return
    imgui.text_wrapped("A text cut at a word, with an ellipsis, to fit a number of lines: a card's title or summary.")
    with imgui_kit.label_column("fit_text"):
        imgui_kit.label("Width")
        imgui.set_next_item_width(imgui_kit.em_size(10))
        _, state.fit_width_em = imgui.slider_float("##width", state.fit_width_em, 4.0, 40.0, "%.0f em")
        imgui_kit.label("Lines")
        imgui.set_next_item_width(imgui_kit.em_size(10))
        _, state.fit_lines = imgui.slider_int("##lines", state.fit_lines, 1, 5)

    text = ("Napoleon's army crossed the Niemen in June 1812 with more than four hundred thousand men; "
            "Minard drew its march to Moscow and its retreat as a band whose width follows the number of "
            "soldiers, and the temperature below it.")
    width = imgui_kit.em_size(state.fit_width_em)
    p = imgui.get_cursor_screen_pos()
    imgui.push_text_wrap_pos(imgui.get_cursor_pos_x() + width)
    imgui.text_unformatted(imgui_kit.fit_text(text, width, state.fit_lines))
    imgui.pop_text_wrap_pos()
    height = imgui.get_text_line_height() * state.fit_lines  # the room the text may take, framed
    imgui.get_window_draw_list().add_rect(p, ImVec2(p.x + width, p.y + height), imgui.get_color_u32(imgui.Col_.border))
    imgui.dummy(ImVec2(0.0, max(0.0, p.y + height - imgui.get_cursor_screen_pos().y)))
    imgui.tree_pop()


def demo_resize_handle() -> None:
    IMGUI_DEMO_MARKER("Widgets/Resize handle")
    if not imgui.tree_node("Resize handle"):
        return
    imgui.text_wrapped("Drag the grip at the bottom-right corner: the widget before it takes the new size. "
                       "Any widget that takes a size: a text field, a child window, a plot.")
    if state.text_size.x == 0:
        state.text_size = imgui_kit.em_to_vec2(20, 4)
        state.child_size = imgui_kit.em_to_vec2(20, 6)
    _, state.resizable_text = imgui.input_text_multiline("##text", state.resizable_text, state.text_size)
    _, state.text_size = imgui_kit.resize_handle("##text_size", state.text_size, imgui_kit.em_to_vec2(6, 2))

    imgui.begin_child("##child", state.child_size, imgui.ChildFlags_.borders)
    imgui.text(f"A child window, {state.child_size.x:.0f} x {state.child_size.y:.0f} px")
    imgui.end_child()
    _, state.child_size = imgui_kit.resize_handle("##child_size", state.child_size, imgui_kit.em_to_vec2(10, 3))
    imgui.tree_pop()


def demo_widgets() -> None:
    IMGUI_DEMO_MARKER("Widgets")
    if not imgui.collapsing_header("Widgets"):
        return
    demo_help_marker()
    demo_icon_button()
    demo_segmented_switch()
    demo_fit_text()
    demo_resize_handle()


# =============================================================================
# Touch
# =============================================================================
def zoomable_canvas(str_id: str, size: ImVec2) -> None:
    """A canvas that zooms with the wheel and pans with a drag, as a plot or an image viewer does. It claims the wheel
    while hovered (imgui.set_item_key_owner), takes a finger's drag at once (imgui_kit.touch.set_item_takes_drags),
    and a pinch (imgui_kit.touch.set_item_takes_pinch: its zoom per notch is 10%, and it uses the wheel's exact value;
    two fingers pan it, with the left button)."""
    io = imgui.get_io()
    p0 = imgui.get_cursor_screen_pos()
    p1 = ImVec2(p0.x + size.x, p0.y + size.y)
    imgui.invisible_button(str_id, size)
    imgui_kit.touch.set_item_takes_drags()
    imgui_kit.touch.set_item_takes_pinch(0.1, imgui.MouseButton_.left, imgui_kit.TouchPinchDelivery_.wheel_continuous)
    if imgui.is_item_active():
        state.canvas_offset = ImVec2(state.canvas_offset.x + io.mouse_delta.x, state.canvas_offset.y + io.mouse_delta.y)
    if imgui.set_item_key_owner(imgui.Key.mouse_wheel_y) and io.mouse_wheel != 0.0:
        # Zoom around the mouse: the point under it stays there
        new_zoom = min(max(state.canvas_zoom * 1.1**io.mouse_wheel, 0.25), 8.0)
        mx, my = io.mouse_pos.x - p0.x, io.mouse_pos.y - p0.y
        state.canvas_offset = ImVec2(mx - (mx - state.canvas_offset.x) * new_zoom / state.canvas_zoom,
                                     my - (my - state.canvas_offset.y) * new_zoom / state.canvas_zoom)
        state.canvas_zoom = new_zoom

    draw_list = imgui.get_window_draw_list()
    rounding = imgui.get_style().frame_rounding
    draw_list.add_rect_filled(p0, p1, imgui.get_color_u32(imgui.Col_.frame_bg), rounding)
    draw_list.push_clip_rect(p0, p1, True)
    step = imgui_kit.em_size() * state.canvas_zoom  # a grid of 1 em at zoom 1
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
    draw_list.pop_clip_rect()
    draw_list.add_rect(p0, p1, imgui.get_color_u32(imgui.Col_.border), rounding)
    draw_list.add_text(ImVec2(p0.x + imgui.get_style().frame_padding.x, p1.y - imgui.get_text_line_height_with_spacing()),
                       imgui.get_color_u32(imgui.Col_.text), f"zoom x{state.canvas_zoom:.2f}")


TOUCH_SETUP_CODE = """imgui.create_context()
imgui_kit.touch.setup()            # the touch layer: swipe, long press, pinch
imgui_kit.setup_wheel_session()    # the wheel stays with the window it scrolls

# The render loop: nothing to add, the kit runs inside imgui.new_frame() and imgui.render().
# - An app that sleeps when idle keeps drawing while imgui_kit.touch.is_animating().
# - A widget that a finger drags: imgui_kit.touch.set_item_takes_drags() right after it.
# - A widget that zooms with the wheel: imgui_kit.touch.set_item_takes_pinch() right after it.
# - A widget that reads the wheel claims it: if imgui.set_item_key_owner(imgui.Key.mouse_wheel_y): ...
# Hello ImGui does the setup itself (RunnerParams.touch_config)."""


def demo_touch() -> None:
    """The settings change the application's touch layer, live. "Simulate a touch source" lets the mouse play a
    finger."""
    IMGUI_DEMO_MARKER("Touch")
    if not imgui.collapsing_header("Touch"):
        return
    io = imgui.get_io()
    imgui.text_wrapped("The gestures of a phone: a finger drags the content (with inertia, and a bounce at the end), "
                       "a long press is a right click, two fingers pinch the font.")
    if imgui.tree_node("The setup code"):
        imgui.text_unformatted(TOUCH_SETUP_CODE)
        imgui.tree_pop()

    config = imgui_kit.touch.get_config()
    with imgui_kit.label_column("touch_settings"):
        if not (io.config_flags & imgui.ConfigFlags_.is_touch_screen):
            imgui_kit.label("On a desktop")
            _, config.simulate_touch = imgui.checkbox("Simulate a touch source", config.simulate_touch)
            imgui.same_line()
            imgui_kit.help_marker("The mouse plays a finger (imgui_kit.TouchConfig.simulate_touch): every gesture works "
                                  "in the zone below, as on a phone:\n\n"
                                  "- Drag up or down to scroll the content. Start moving as soon as you press, as with "
                                  "a finger.\n"
                                  "- Press and hold, then release: a long press, which opens the zone's context menu "
                                  "(a right click).")
        imgui_kit.label("Swipe")
        scroll_modes = ["Touch", "Always", "Off"]
        next_line_if_too_wide(imgui_kit.segmented_switch_width(scroll_modes))
        _, config.scroll_mode = imgui_kit.segmented_switch("##scroll_mode", config.scroll_mode, scroll_modes)
        imgui.same_line()
        imgui_kit.help_marker("Touch: the swipe follows a finger only. Always: the mouse's left button drags the "
                              "content too, while the mouse stays a mouse.")
        imgui_kit.label("Pinch")
        pinch_modes = ["Font scale", "Off"]
        next_line_if_too_wide(imgui_kit.segmented_switch_width(pinch_modes))
        _, config.pinch_mode = imgui_kit.segmented_switch("##pinch_mode", config.pinch_mode, pinch_modes)
        imgui_kit.label("Long press")
        _, config.long_press_is_right_click = imgui.checkbox("is a right click", config.long_press_is_right_click)
        imgui_kit.label("Scroll bars")
        _, config.thin_scrollbars = imgui.checkbox("thin on a touch screen", config.thin_scrollbars)

    imgui.begin_child("##touch_zone", ImVec2(0.0, imgui_kit.em_size(16)), imgui.ChildFlags_.borders)
    imgui.bullet()
    imgui.text_wrapped("Swipe: a finger that drags this zone scrolls it, with inertia, and a bounce at the end.")
    imgui.bullet()
    imgui.text_wrapped("Tap: a click, when the finger lifts.")
    imgui.bullet()
    imgui.text_wrapped("Hold, then drag: the widget under the finger takes it (the slider below).")
    imgui.bullet()
    imgui.text_wrapped("Long press, then lift: a right click (this zone's context menu).")
    imgui.bullet()
    imgui.text_wrapped("Two fingers: a pinch scales the font (on the canvas, it zooms the canvas); moved together, a "
                       "right drag.")
    imgui.set_next_item_width(imgui_kit.em_size(12))
    _, state.touch_value = imgui.slider_float("a short hold, then a drag", state.touch_value, 0.0, 1.0)
    imgui.same_line()
    imgui_kit.help_marker("This slider does not call imgui_kit.touch.set_item_takes_drags(): to drag it with a finger, "
                          "hold it a moment first (a ring shows when the hold took effect). A drag that starts at once "
                          "scrolls the zone. The canvas below reacts at once.")

    zoomable_canvas("##canvas", imgui_kit.em_to_vec2(16, 8))
    imgui.same_line()
    imgui_kit.help_marker("A canvas that zooms and pans, as a plot or an image viewer does:\n\n"
                          "- It calls imgui_kit.touch.set_item_takes_drags() right after it: a drag that starts on it "
                          "pans it at once. So the zone cannot be scrolled from inside the canvas.\n"
                          "- It claims the wheel while hovered: if imgui.set_item_key_owner(imgui.Key.mouse_wheel_y). "
                          "With the wheel session, a wheel that scrolls the zone keeps scrolling it when the canvas "
                          "passes under the mouse; a wheel that starts on the canvas zooms it.\n"
                          "- It calls imgui_kit.touch.set_item_takes_pinch(): a pinch on it zooms it, instead of the "
                          "font, and two fingers moved together pan it.")
    if imgui.begin_popup_context_window("##zone_menu"):
        imgui.text_unformatted("The zone's context menu: a right click, or a long press")
        imgui.end_popup()

    # A child that scrolls sideways: a swipe inside scrolls it, not the zone. Its buttons count their taps. Its slider
    # takes the sideways drags (imgui_kit.touch.set_item_takes_drags_along): a sideways drag on it moves it at once
    imgui.text_wrapped("A sideways swipe scrolls this row; a tap clicks a button; a sideways drag moves the slider:")
    imgui.begin_child("##sideways", ImVec2(0.0, imgui_kit.em_size(5)), imgui.ChildFlags_.borders,
                      imgui.WindowFlags_.horizontal_scrollbar)
    card_width = max(imgui_kit.em_size(6), imgui.get_content_region_avail().x * 0.3)  # 3 per screen: it scrolls
    imgui.set_next_item_width(card_width)
    _, state.row_value = imgui.slider_float("##row_slider", state.row_value, 0.0, 1.0)
    imgui_kit.touch.set_item_takes_drags_along(imgui_kit.TouchAxis_.x)
    for i in range(len(state.taps)):
        imgui.same_line()
        if imgui.button(f"Card {i + 1}\n{state.taps[i]} taps###card{i}", ImVec2(card_width, imgui_kit.em_size(3))):
            state.taps[i] += 1
    imgui.end_child()
    for i in range(1, 9):
        imgui.text(f"More content, to scroll ({i})")
    imgui.end_child()
    # is_animating(): an application that sleeps when nothing happens keeps drawing frames meanwhile
    imgui.text(f"Moving on its own: {'yes' if imgui_kit.touch.is_animating() else 'no'}")


def demo_touch_keyboard() -> None:
    """The phone's keyboard, in a browser: the fields of all kinds, one of them in a child that scrolls."""
    IMGUI_DEMO_MARKER("Touch keyboard")
    if not imgui.collapsing_header("Touch keyboard"):
        return
    imgui.text_wrapped("In a browser on a phone: tap a field, then the keyboard button that shows next to it (or the "
                       "field again). The phone's keyboard opens, and a full-screen window keeps out of it "
                       "(imgui_kit.touch.get_keyboard_insets()). Hello ImGui sets it up (in C++: "
                       "ImGuiTouch::SetupEmscriptenKeyboard()).")
    _, state.keyboard_line = imgui.input_text_with_hint("text", "type here", state.keyboard_line)
    _, state.keyboard_lines = imgui.input_text_multiline("lines", state.keyboard_lines,
                                                         ImVec2(0.0, imgui_kit.em_size(5)))

    imgui.text_wrapped("A field in a child that scrolls: it stays above the keyboard.")
    imgui.begin_child("##keyboard_child", ImVec2(0.0, imgui_kit.em_size(10)), imgui.ChildFlags_.borders)
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
    imgui.text_wrapped("ImGuiKit: small, standalone additions to Dear ImGui")
    if state.font_size == 0.0:
        state.font_size = imgui.get_style().font_size_base
    demo_toolbar()
    imgui.separator()
    imgui.push_font(None, state.font_size)
    demo_em_units()
    demo_layout()
    demo_widgets()
    demo_touch()
    demo_touch_keyboard()
    imgui.pop_font()


def gui() -> None:
    show_demo_contents()


def main() -> None:
    immapp.run(gui, window_title="imgui_kit demo", window_size=(600, 750), with_markdown=True)


if __name__ == "__main__":
    main()
