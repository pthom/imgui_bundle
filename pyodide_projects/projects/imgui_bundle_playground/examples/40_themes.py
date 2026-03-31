"""# Themes

Dear ImGui Bundle supports theming at two levels:

- **Hello ImGui themes**: high-level themes like Darcula, Cherry, etc. Apply with `hello_imgui.apply_theme()`
- **ImGui style**: fine-grained control over colors and spacing via `imgui.get_style()`

**Links:**
- [Theming documentation](https://pthom.github.io/imgui_bundle/)
"""
# TODO: adapt from demo_themes.py (fix floating demo window)
from imgui_bundle import imgui, immapp

def gui():
    imgui.text("TODO: Themes demo")

immapp.run(gui, window_title="Themes")
