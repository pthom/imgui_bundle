"""
On a touch screen: the gestures of a phone, in the browser

The gestures of a phone in the browser: a swipe, a tap, a long press, a pinch, the keyboard.
On a mobile or a tablet, Hello ImGui turns a finger into what its user expects: a swipe scrolls,
a tap clicks, a held finger opens a context menu, a pinch scales the app (its font), two fingers pan, and a keyboard button
appears next to a text field.

Nothing to write in the app: the gestures come from `RunnerParams.touch_scroll_mode`, `touch_pinch_mode` and
`touch_long_press_is_right_click`. On a desktop, tick "Simulate a touch source" to try them with the mouse.
"""

from typing import Any

import numpy as np
from imgui_bundle import ImVec2, ImVec4, hello_imgui, imgui, immapp, immvision, implot, rich_md
from imgui_bundle import register_demos_assets_folder

register_demos_assets_folder()

GESTURES = """
- **Swipe** anywhere, on this text or on the button below: the content scrolls, with inertia, and a bounce at the end.
- **Tap** a button: a click. **Hold** a slider a moment, then drag it.
- **Hold** a word of this text half a second, until a ring shows, then lift: the menu of a right click (Copy, Select All). The same on the button: its menu.
- **Pinch** with two fingers: the app (its font) scales.
- **Drag with two fingers**: a right drag, which box-selects in the plot.
- **Tap a text field**, then the keyboard button that appears under it: type, move the caret from the keyboard's space bar.

> [!NOTE]
> * Those gestures are only available when running an application with hello_imgui or immapp. They are not available when using your own backend / loop (such as with a pure Python backend).
> * They are enabled by default. You do not need to change anything to get them.
> * Configure them with `RunnerParams.touch_scroll_mode`, `touch_pinch_mode` and `touch_long_press_is_right_click`.
"""

PLOTS = """
- **Box select**: a right drag on a desktop, a **two-finger drag** on a touch screen.
- **Pan**: a left drag on a desktop. With a finger, **hold** a moment, then drag (a swipe scrolls the page).
- The guide lines and the box of the second plot: drag them the same way.
- A double click (a double tap) fits the plot.
"""

IMAGES = """
- **The first image** resizes by its bottom right corner: hold the corner, then drag.
- **The second one** pans by a drag (hold, then drag), and zooms with the mouse wheel or its + / - buttons.
- A pinch scales the app, not the image.
"""

BUTTON_NAMES = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
PHONE_WIDTH_EM = 26  # on a desktop, the page shows in a column of this width: the layout of a phone

# The state of the widgets
simulate_touch = False
clicks = 0
menu_choice = ""
slider = 0.5
text = "abc def ghi"
lines = "one\ntwo\nthree"
button_clicks = [0] * len(BUTTON_NAMES)
points = np.random.RandomState(42).rand(2, 40)
guide_x, guide_y = 0.5, 0.5  # the draggable lines of the second plot
box = [0.2, 0.2, 0.6, 0.7]  # its draggable rectangle: x1, y1, x2, y2
images: dict[str, Any] = {}  # the images and their display params, loaded at the first frame
tennis_size = ImVec2(0, 0)  # the size of the resizable image, chosen by the user (set at the first frame)


def section(title: str) -> None:
    """A section title, with some air above it"""
    imgui.dummy(hello_imgui.em_to_vec2(0, 1))
    rich_md.render(f"## {title}")


def gui() -> None:
    on_phone = bool(imgui.get_io().config_flags & imgui.ConfigFlags_.is_touch_screen)
    if on_phone:
        page()
        return
    # A desktop: a column as wide as a phone, so that the layout is the phone's (the images take the width)
    width = min(hello_imgui.em_size(PHONE_WIDTH_EM), imgui.get_content_region_avail().x)
    imgui.begin_child("phone", ImVec2(width, 0), imgui.ChildFlags_.borders)
    page()
    imgui.end_child()


def page() -> None:
    global simulate_touch, clicks, menu_choice, slider, text, lines, guide_x, guide_y
    io = imgui.get_io()
    if simulate_touch:
        io.add_mouse_source_event(imgui.MouseSource.touch_screen)

    # The help, in a colored child: a swipe inside scrolls it, a swipe elsewhere scrolls the page
    rich_md.render("# On a touch screen")
    section("Vertical swipe")
    bg_col_orig = imgui.get_style_color_vec4(imgui.Col_.child_bg)
    mixed_color = ImVec4(0, 0.5, 1, 1)
    bg_col = bg_col_orig * 0.6 + mixed_color * 0.4
    imgui.push_style_color(imgui.Col_.child_bg, bg_col)
    imgui.begin_child("Help", ImVec2(0, hello_imgui.em_size(10)))
    rich_md.render(GESTURES)
    imgui.end_child()
    imgui.pop_style_color()
    if not (io.config_flags & imgui.ConfigFlags_.is_touch_screen):
        # A desktop, in the browser too: the mouse plays the finger (the source applies to the events that follow)
        changed, simulate_touch = imgui.checkbox("Simulate a touch source", simulate_touch)
        if changed and not simulate_touch:
            io.add_mouse_source_event(imgui.MouseSource.mouse)
        imgui.same_line()
        sources = {imgui.MouseSource.mouse: "mouse", imgui.MouseSource.touch_screen: "touch screen", imgui.MouseSource.pen: "pen"}
        imgui.text_disabled(f"(the input is a {sources.get(io.mouse_source, '?')})")

    # A child that scrolls sideways: a swipe inside scrolls it, not the page; big buttons count their taps
    section("Horizontal swipe")
    imgui.begin_child("Planets", hello_imgui.em_to_vec2(0, 7), imgui.ChildFlags_.borders, imgui.WindowFlags_.horizontal_scrollbar)
    button_width = max(hello_imgui.em_size(7), imgui.get_content_region_avail().x * 0.3)  # three per screen: the child scrolls on a desktop too
    for i, name in enumerate(BUTTON_NAMES):
        if i > 0:
            imgui.same_line()
        if imgui.button(f"{name}\n{button_clicks[i]} taps##planet{i}", ImVec2(button_width, hello_imgui.em_size(5))):
            button_clicks[i] += 1
    imgui.end_child()

    # A button with a menu, a counter, a slider, the text fields (the keyboard of a phone)
    section("Widgets")
    # The labels at the left of the widgets
    def label(name: str) -> None:
        imgui.align_text_to_frame_padding()
        imgui.text(name)
        imgui.same_line(hello_imgui.em_size(7))

    label("Context menu")
    if imgui.button("Right click, or hold"):
        clicks += 1
    if imgui.begin_popup_context_item("button_menu"):
        for choice in ("Reset the counter", "Add ten"):
            if imgui.menu_item_simple(choice):
                menu_choice = choice
                clicks = 0 if choice.startswith("Reset") else clicks + 10
        imgui.end_popup()
    imgui.same_line()
    imgui.text(f"{clicks} clicks" + (f", last menu choice: {menu_choice}" if menu_choice else ""))


    # The widgets take the remaining width (-1): ImGui's default width is 65% of the window, from where the item starts
    label("Slider")
    imgui.set_next_item_width(-1)
    _, slider = imgui.slider_float("##slider", slider, 0.0, 1.0)
    label("Text field")
    imgui.set_next_item_width(-1)
    _, text = imgui.input_text("##text", text)
    label("Multiline edit")
    _, lines = imgui.input_text_multiline("##lines", lines, ImVec2(-1, hello_imgui.em_size(4)))

    # The plots: box select (a right drag: two fingers), pan (a left drag: hold, then drag), draggable tools
    section("Plots")
    rich_md.render(PLOTS)
    # ImPlot: a size of 0 is its default plot size (400 px wide), -1 the remaining width
    if implot.begin_plot("Box select, pan", ImVec2(-1, hello_imgui.em_size(14))):
        implot.plot_scatter("points", points[0], points[1])
        implot.end_plot()
    if implot.begin_plot("Drag the lines and the box", ImVec2(-1, hello_imgui.em_size(14))):
        implot.setup_axes_limits(0, 1, 0, 1)
        _, guide_x, *_ = implot.drag_line_x(0, guide_x, ImVec4(1, 0.5, 0, 1), thickness=3)
        _, guide_y, *_ = implot.drag_line_y(1, guide_y, ImVec4(0, 0.8, 0.4, 1), thickness=3)
        _, box[0], box[1], box[2], box[3], *_ = implot.drag_rect(2, box[0], box[1], box[2], box[3], ImVec4(0.3, 0.6, 1, 1))
        implot.plot_scatter("points", points[0], points[1])
        implot.end_plot()

    # The images (ImmVision): a resizable one, one that pans and zooms
    section("Images")
    rich_md.render(IMAGES)
    if not images:
        images["tennis"] = immvision.im_read(hello_imgui.asset_file_full_path("images/tennis.jpg"))  # RGB(A), no OpenCV
        images["bear"] = immvision.im_read(hello_imgui.asset_file_full_path("images/bear_transparent.png"))
        images["bear_params"] = immvision.ImageParams()
        # A negative size is the remaining width of the window (as ImGui's item widths), resolved at the first frame
        tennis_size.x, tennis_size.y = -1, hello_imgui.em_size(14)
        images["bear_params"].image_display_size = (-1, 0)  # the height from the image's aspect ratio
    immvision.image_display_resizable("Tennis", images["tennis"], size=tennis_size)  # the size is in and out
    immvision.image("Bear", images["bear"], images["bear_params"])


def main() -> None:
    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "On a touch screen"
    runner_params.app_window_params.window_geometry.size = (500, 800)
    runner_params.callbacks.show_gui = gui
    addons = immapp.AddOnsParams(with_markdown=True, with_implot=True)
    immapp.run(runner_params, addons)


if __name__ == "__main__":
    main()
