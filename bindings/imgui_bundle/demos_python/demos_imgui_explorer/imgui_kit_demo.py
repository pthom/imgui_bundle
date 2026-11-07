"""imgui_kit: the demo

Small, standalone additions to Dear ImGui: em units, a row that fills its line, aligned groups, columns, a label
column, a flow, a help marker, icon buttons, a segmented switch. The Python twin of imgui_kit_demo.cpp, section by
section.
"""
###############################################################################
# imgui_kit_demo.py is a port of imgui_kit_demo.cpp (https://github.com/pthom/imgui_kit). In Python, the
# Begin/End pairs are also context managers: `with imgui_kit.fill_row("slice") as row: ... row.tail() ...`.
###############################################################################
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


state = _State()


# =============================================================================
# Toolbar: theme, font size, frame rounding
# =============================================================================
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
        changed, state.theme = imgui_kit.segmented_switch("##theme", state.theme, ["App", "Dark", "Light", "Classic"])
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

        imgui_kit.label("Font size")
        imgui.set_next_item_width(imgui_kit.em_size(8))
        _, state.font_size = imgui.slider_float("##font_size", state.font_size, 8.0, 40.0, "%.0f px")

        imgui_kit.label("Frame rounding")
        imgui.set_next_item_width(imgui_kit.em_size(8))
        _, style.frame_rounding = imgui.slider_float("##rounding", style.frame_rounding, 0.0, 12.0, "%.0f px")
        imgui.same_line()
        imgui_kit.help_marker("The style's frame_rounding: imgui.get_style().frame_rounding. Buttons, sliders, input "
                              "fields and the segmented switch round their corners with it. 0 gives square frames; "
                              "half the frame's height gives a pill.")
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
               "Sand", "Honey", "Midnight blue", "Rose", "Turquoise", "Custom"]
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
# Demo window
# =============================================================================
def show_demo_contents() -> None:
    imgui.text("ImGuiKit: small, standalone additions to Dear ImGui")
    if state.font_size == 0.0:
        state.font_size = imgui.get_style().font_size_base
    demo_toolbar()
    imgui.separator()
    imgui.push_font(None, state.font_size)
    demo_em_units()
    demo_layout()
    demo_widgets()
    imgui.pop_font()


def gui() -> None:
    show_demo_contents()


def main() -> None:
    immapp.run(gui, window_title="imgui_kit demo", window_size=(600, 750), with_markdown=True)


if __name__ == "__main__":
    main()
