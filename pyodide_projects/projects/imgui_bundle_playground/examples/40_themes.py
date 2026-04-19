"""# Theming

Dear ImGui Bundle supports theming at two levels:

**Hello ImGui themes** provide complete, pre-designed looks. Apply one with a single line:
```python
hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.darcula)  # or apply_tweaked_theme (see below)
```
**Tweaks** let you fine-tune colors, rounding, spacing, and other style variables.
"""
from imgui_bundle import imgui, immapp, hello_imgui, imgui_md, ImVec2


def gui_select_theme() -> None:
    """Shows hello_imgui's theme selector and tweak panel
    Note: to select a theme at startup simply call
        hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.darcula)
    """
    tweaked_theme = hello_imgui.get_runner_params().imgui_window_params.tweaked_theme
    changed = hello_imgui.show_theme_tweak_gui(tweaked_theme)
    if changed:
        hello_imgui.apply_tweaked_theme(tweaked_theme)


def gui_preview_theme_with_widgets() -> None:
    """Show a collection of widgets to demonstrate the effect of the theme"""
    # Right: sample widgets to preview the theme
    imgui.begin_child("##preview")
    imgui.text("Preview widgets:")
    imgui.separator()

    imgui.button("Button")
    imgui.same_line()
    imgui.button("Another")
    imgui.same_line()
    imgui.small_button("Small")

    _ = imgui.checkbox("Checkbox", True)
    imgui.same_line()
    _ = imgui.checkbox("Unchecked", False)

    em = hello_imgui.em_size()
    imgui.set_next_item_width(em * 12)
    _ = imgui.slider_float("Slider", 0.5, 0.0, 1.0)

    imgui.set_next_item_width(em * 12)
    _ = imgui.input_text("Input", "Hello")

    imgui.set_next_item_width(em * 12)
    _ = imgui.combo(
        "Combo", 0,
        ["Option A", "Option B", "Option C"])

    if imgui.collapsing_header("Collapsing Header"):
        imgui.text("Inside a collapsing header")
        imgui.bullet_text("Bullet item 1")
        imgui.bullet_text("Bullet item 2")

    imgui.progress_bar(0.7, (em * 12, 0), "70%")

    if imgui.tree_node("Tree Node"):
        imgui.text("Tree content")
        imgui.tree_pop()

    imgui_md.render_unindented(r"""
#### Markdown examples
|          |                                                                  |
|----------|-------------------------------------------------------------------------|
| Emphasis | *italic*, **bold**, ***both***                                          |
| Code     | `inline_code()`                                                         |
| Links    | [Example](https://example.com)                                          |
| Math     | $\displaystyle \sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}$     |
| Image    | ![random image](https://picsum.photos/160/120)                          |

```python
print("This is a code block")
```
""")


    imgui.end_child()


def gui_layout() -> None:
    """Main Gui function
    - Renders the Markdown doc
    - Creates two panel (child_window):
        - on the left, the theme selector
        - on the right, a widget collection to preview the theme
    """
    # Documentation panel
    immapp.render_markdown_doc_panel(__doc__, height_em=14)

    avail = imgui.get_content_region_avail()

    # Left: theme selector / tweak panel (resizable)
    left_w = avail.x * 0.5  # initial width
    imgui.begin_child("##theme_tweak", size=(left_w, 0),
        child_flags=imgui.ChildFlags_.resize_x)
    gui_select_theme()
    imgui.end_child()

    # Make sure our two panels are horizontally side by side
    imgui.same_line()

    # Right: preview with widgets
    imgui.begin_child("##preview")
    gui_preview_theme_with_widgets()
    imgui.end_child()


##########################################################################
#    Define the app initial theme
##########################################################################
def setup_my_theme():
    """Example of theme customization at App startup
    This function is called in the callback `setup_imgui_style` in order to apply a custom theme:
        runner_params.callbacks.setup_imgui_style = setup_my_theme()
    """
    # Apply default style
    hello_imgui.imgui_default_settings.setup_default_imgui_style()
    # Create a tweaked theme
    tweaked_theme = hello_imgui.ImGuiTweakedTheme()
    tweaked_theme.theme = hello_imgui.ImGuiTheme_.material_flat
    tweaked_theme.tweaks.rounding = 10.0
    # Apply the tweaked theme
    hello_imgui.apply_tweaked_theme(tweaked_theme)  # Note: you can also push/pop the theme in order to apply it only to a specific part of the Gui:  hello_imgui.push_tweaked_theme(tweaked_theme) / hello_imgui.pop_tweaked_theme()
    # Then apply further modifications to ImGui style
    imgui.get_style().item_spacing = ImVec2(6, 4)  # Reduce spacing between items ((8, 4) by default)
    imgui.get_style().set_color_(imgui.Col_.text, (0.8, 0.8, 0.85, 1.0))  # Change text color


def main():
    # Here we use the fully customizable to set up an application:
    # 1. Define and populate hello_imgui RunnerParams
    #    (in this example, we change the theme at startup)
    params = hello_imgui.RunnerParams()
    params.callbacks.show_gui = gui_layout
    params.callbacks.setup_imgui_style = setup_my_theme
    params.app_window_params.window_geometry.size = (1000, 700)
    params.app_window_params.window_title = "Themes"
    params.ini_disable = True
    # 2. Define which addons we want to activate
    addons = immapp.AddOnsParams()
    addons.with_markdown = True
    addons.with_latex = True
    # 3. Run the app
    immapp.run(params, addons)


if __name__ == "__main__":
    main()
