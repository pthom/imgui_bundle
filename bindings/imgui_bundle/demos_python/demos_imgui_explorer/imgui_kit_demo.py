"""imgui_kit: the demo

Small, standalone additions to Dear ImGui: em units, a row that fills its line, aligned groups, a flow, a help
marker, icon buttons, a segmented switch. The Python twin of imgui_kit_demo.cpp, section by section.
"""
###############################################################################
# imgui_kit_demo.py is a port of imgui_kit_demo.cpp (https://github.com/pthom/imgui_kit). In Python, the
# Begin/End pairs are also context managers: `with imgui_kit.fill_row("slice") as row: ... row.tail() ...`.
###############################################################################
from imgui_bundle import imgui, imgui_kit, immapp


def IMGUI_DEMO_MARKER(section: str) -> None:
    """Marker for the Explorer. Maps sections to source code."""
    pass


class _State:
    font_size = 0.0
    slice = 37
    text = "An InputText fills the line too"
    preset = 0
    zoom = 1.0
    view = 0
    unit = 1


state = _State()


# =============================================================================
# Em units
# =============================================================================
def demo_em_units() -> None:
    IMGUI_DEMO_MARKER("Em units")
    if not imgui.collapsing_header("Em units"):
        return
    imgui.text_wrapped("Sizes in em follow the font: the first button is 8 em wide and 2 em high, on any screen. "
                       "Change the font size: it grows with the text, as a standard button does. "
                       "The last button keeps its size in pixels: at a large font, its label gets cut.")
    if state.font_size == 0.0:  # 0: the current size, unchanged
        state.font_size = imgui.get_style().font_size_base
    imgui.set_next_item_width(imgui_kit.em_size(12))
    _, state.font_size = imgui.slider_float("Font size", state.font_size, 8.0, 40.0, "%.0f px")
    imgui.same_line()
    if imgui.button("Reset"):
        state.font_size = imgui.get_style().font_size_base

    imgui.push_font(None, state.font_size)
    imgui.button("8 x 2 em", imgui_kit.em_to_vec2(8, 2))
    imgui.same_line()
    imgui.button("A standard button")
    imgui.same_line()
    imgui.button("100 x 30 px", (100, 30))
    imgui.same_line()
    imgui_kit.help_marker("em_to_vec2(8, 2) gives the size in pixels, from the current font size.")
    imgui.text(f"1 em = {imgui_kit.em_size():.1f} px")
    imgui.pop_font()


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


def demo_flow() -> None:
    IMGUI_DEMO_MARKER("Layout/Flow")
    if not imgui.tree_node("Flow"):
        return
    imgui.text_wrapped("The buttons stay on a line while they fit. Resize the window: they flow to the next line.")
    presets = ["Lung", "Mediastinum", "Bone", "Full range", "Brain", "Liver", "Soft tissue",
               "Abdomen", "Spine", "Angiography", "Stroke", "Temporal bone", "Custom"]
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
    views = ["Demo", "Code"]
    _, state.view = imgui_kit.segmented_switch("##view", state.view, views)
    imgui.same_line()
    imgui.text(f"showing: {views[state.view]}")
    _, state.unit = imgui_kit.segmented_switch("##unit", state.unit, ["mm", "cm", "inch"])
    imgui.tree_pop()


def demo_widgets() -> None:
    IMGUI_DEMO_MARKER("Widgets")
    if not imgui.collapsing_header("Widgets"):
        return
    demo_help_marker()
    demo_icon_button()
    demo_segmented_switch()


# =============================================================================
# Demo window
# =============================================================================
def show_demo_contents() -> None:
    imgui.text("ImGuiKit: small, standalone additions to Dear ImGui")
    imgui.separator()
    demo_em_units()
    demo_layout()
    demo_widgets()


def gui() -> None:
    show_demo_contents()


def main() -> None:
    immapp.run(gui, window_title="imgui_kit demo", window_size=(600, 750), with_markdown=True)


if __name__ == "__main__":
    main()
