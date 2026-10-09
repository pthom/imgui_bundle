"""# What is an Immediate GUI

With [Dear ImGui](https://github.com/ocornut/imgui), your GUI code is **simple and direct**: no widget trees,
no callbacks, no state synchronization. You call functions to create widgets, and they return the current
value. That's it.

For example, the first "Volume" widget below is created with the code:
```python
_volume_changed, s.volume = imgui.slider_float("Volume", v=s.volume, v_min=0.0, v_max=12.0, format="%.1f")
```

The widget is drawn, and if the user moved the slider, `changed` is True and `value` is updated.
This function is called every frame - the UI is rebuilt from scratch each time. This is the
**immediate mode** paradigm.

**Try it:** edit any value below and see the result update instantly. Then look at the code -
notice how each widget is just one line, and state is just plain Python variables.

**Links:**
- [What is Dear ImGui Bundle?](https://imgui-bundle.pages.dev/doc/intro/what-is-imgui-bundle/)
- [Immediate Mode Explained](https://imgui-bundle.pages.dev/doc/intro/imm-gui/)
- [Dear ImGui Explorer](https://pthom.github.io/imgui_explorer)
"""
from imgui_bundle import imgui, immapp, hello_imgui, rich_md


AVAILABLE_ITEMS = ["Apple", "Banana", "Cherry", "Date"]


class AppState:
    """All the app state in one place - just plain Python attributes."""
    name: str = "World"
    volume: float = 4.5
    choice: int = 1
    count: int = 0
    selected_item: int = 1
    show_extra: bool = False
    # color is initialized in __init__ (as list are mutable types)
    color: list[float]
    def __init__(self):
        self.color = [0.4, 0.7, 1.0, 1.0]


def gui(state: AppState) -> None:
    # First, the documentation: open at first, it folds to its first paragraph as soon as the user tries the widgets
    intro_options = rich_md.FoldingTextOptions()
    intro_options.fold_on_click_elsewhere = True
    rich_md.render_folding("intro", __doc__, intro_options)
    imgui.separator()

    # s will contain the state (that is modified directly by the widgets)
    s = state
    # em <=> equivalent to the em CSS unit
    em = imgui.get_font_size()


    # Click me button
    if imgui.button("Click me!"):  # show the button
        # And handle its click action immediately!
        s.count += 1
    # Use imgui.same_line() to draw the next widget on the same line
    imgui.same_line()
    imgui.text(f"Clicked {s.count} times")
    imgui.separator()


    # Widgets that manipulate a value will return a tuple of two values,
    # such as the slider below (`slider_float`):
    #     - was the widget just used
    #     - what is the new value
    # Thus, we store the output as
    #     _volume_changed, s.volume
    # Later examples will use a shorter form if we do not care about the first (was it used):
    #     _, s.volume
    _volume_changed, s.volume = imgui.slider_float(
        label="Volume", v=s.volume, v_min=0.0, v_max=12.0, format="%.1f")
    imgui.separator()  # a horizontal separator line

    # Text input
    #   set_next_item_width: reduce the width of the input_text
    #                        (which occupies the full width by default)
    imgui.set_next_item_width(em * 15)
    _, s.name = imgui.input_text(label="Your name", str=s.name)
    imgui.text(f"Hello, {s.name}!")
    imgui.separator()

    # Color picker
    # Note: hello_imgui.em_size(15) is equivalent to em * 15
    imgui.set_next_item_width(hello_imgui.em_size(15))
    _, s.color = imgui.color_edit4("Accent color", s.color)
    imgui.separator()

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
    _, s.selected_item = imgui.combo(
        "Fruit", s.selected_item, AVAILABLE_ITEMS)
    imgui.separator()

    # Collapsible section
    _, s.show_extra = imgui.checkbox("Show extra info", s.show_extra)
    if s.show_extra:
        imgui.indent()
        imgui.text_disabled("This section is conditionally visible.")
        imgui.text(f"Mode: {['Easy', 'Medium', 'Hard'][s.choice]}")
        imgui.text(f"Fruit: {AVAILABLE_ITEMS[s.selected_item]}")
        imgui.unindent()


def main():
    state = AppState()
    immapp.run(
        lambda: gui(state),
        window_size=(1000, 700),
        window_title="What is an Immediate GUI",
        with_markdown=True
    )


if __name__ == "__main__":
    main()
