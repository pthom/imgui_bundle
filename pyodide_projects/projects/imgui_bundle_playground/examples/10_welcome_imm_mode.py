"""# Welcome to Immediate Mode GUI

With Dear ImGui, your GUI code is **simple and direct**: no widget trees, no callbacks, no state synchronization.
You call functions to create widgets, and they return the current value. That's it.

```python
changed, value = imgui.slider_float("Speed", value, 0, 100)
```

The widget is drawn, and if the user moved the slider, `changed` is True and `value` is updated.
This function is called every frame - the UI is rebuilt from scratch each time. This is the
**immediate mode** paradigm.

**Try it:** edit any value below and see the result update instantly. Then look at the code -
notice how each widget is just one line, and state is just plain Python variables.

**Links:**
- [What is Dear ImGui Bundle?](https://pthom.github.io/imgui_bundle/intro/what-is-imgui-bundle/)
- [Immediate Mode Explained](https://pthom.github.io/imgui_bundle/intro/imm-gui/)
- [Dear ImGui in the Explorer](https://traineq.org/imgui_bundle_explorer/?lib=imgui)
"""
from imgui_bundle import imgui, imgui_md, immapp, hello_imgui, ImVec2, ImVec4


AVAILABLE_ITEMS = ["Apple", "Banana", "Cherry", "Date"]


class AppState:
    """All the app state in one place - just plain Python attributes."""
    name: str = "World"
    volume: float = 0.5
    is_active: bool = True
    choice: int = 1
    count: int = 0
    selected_item: int = 1
    show_extra: bool = False
    # color is initialized in __init__ (as list are mutable types)
    color: list
    def __init__(self):
        self.color = [0.4, 0.7, 1.0, 1.0]




def render_top_doc(doc: str, height_em: float | None):
    # tweaked_theme = hello_imgui.ImGuiTweakedTheme()
    # tweaked_theme.theme = hello_imgui.ImGuiTheme_.gray_variations_darker
    # tweaked_theme.tweaks.rounding = 0.0
    # hello_imgui.push_tweaked_theme(tweaked_theme)
    bg_col = imgui.get_style_color_vec4(imgui.Col_.text)
    bg_col.x = 1.0
    bg_col.y = 0.0
    imgui.push_style_color(imgui.Col_.text, bg_col)

    imgui.begin_child("##doc", hello_imgui.em_to_vec2(0, height_em), imgui.ChildFlags_.borders | imgui.ChildFlags_.resize_y)
    imgui_md.render_unindented(doc)
    imgui.end_child()

    imgui.pop_style_color()

    # hello_imgui.pop_tweaked_theme()


def gui(state: AppState) -> None:
    s = state

    # Top: docstring as Markdown
    # doc_h = avail.y * 0.6
    # imgui.begin_child("##doc", ImVec2(0, doc_h), imgui.ChildFlags_.borders | imgui.ChildFlags_.resize_y)
    # imgui.push_style_color(imgui.Col_.frame_bg, ImVec4(0.5, 0, 0, 1))
    # imgui_md.render(__doc__)
    # imgui.pop_style_color()
    # imgui.end_child()
    render_top_doc(__doc__, 20)

    # Bottom: interactive widgets
    imgui.begin_child("##widgets")

    # Text input
    imgui.set_next_item_width(hello_imgui.em_size(15))
    _, s.name = imgui.input_text("Your name", s.name)
    imgui.text(f"Hello, {s.name}!")

    imgui.separator()

    # Slider
    em = hello_imgui.em_size()
    imgui.set_next_item_width(em * 15)
    _, s.volume = imgui.slider_float("Volume", s.volume, 0.0, 1.0, "%.2f")

    # Progress bar shows the same value
    imgui.progress_bar(s.volume, ImVec2(em * 15, 0), f"{s.volume:.0%}")

    imgui.separator()

    # Color picker
    imgui.set_next_item_width(em * 15)
    _, s.color = imgui.color_edit4("Accent color", s.color)

    # Show a colored button using the selected color
    r, g, b, a = s.color[0], s.color[1], s.color[2], s.color[3]
    imgui.push_style_color(imgui.Col_.button, ImVec4(r, g, b, a))
    imgui.push_style_color(imgui.Col_.button_hovered,
        ImVec4(min(r * 1.2, 1.0), min(g * 1.2, 1.0), min(b * 1.2, 1.0), a))
    if imgui.button("Click me!"):
        s.count += 1
    imgui.pop_style_color(2)
    imgui.same_line()
    imgui.text(f"Clicked {s.count} times")

    imgui.separator()

    # Checkbox
    _, s.is_active = imgui.checkbox("Active", s.is_active)

    # Radio buttons
    imgui.same_line()
    imgui.text("  Mode:")
    imgui.same_line()
    if imgui.radio_button("Easy", s.choice == 0):
        s.choice = 0
    imgui.same_line()
    if imgui.radio_button("Medium", s.choice == 1):
        s.choice = 1
    imgui.same_line()
    if imgui.radio_button("Hard", s.choice == 2):
        s.choice = 2

    # Combo (dropdown)
    imgui.set_next_item_width(em * 15)
    _, s.selected_item = imgui.combo("Fruit", s.selected_item, AVAILABLE_ITEMS)

    imgui.separator()

    # Collapsible section
    _, s.show_extra = imgui.checkbox("Show extra info", s.show_extra)
    if s.show_extra:
        imgui.indent()
        imgui.text_colored(ImVec4(0.5, 0.8, 1.0, 1.0), "This section is conditionally visible.")
        imgui.text(f"Active: {s.is_active} | Mode: {['Easy', 'Medium', 'Hard'][s.choice]} | Fruit: {s.items[s.selected_item]}")
        imgui.unindent()

    imgui.end_child()


if __name__ == "__main__":
    state = AppState()
    immapp.run(
        lambda: gui(state),
        window_size=(1000, 700),
        window_title="Welcome to Immediate Mode",
        with_markdown=True
    )
