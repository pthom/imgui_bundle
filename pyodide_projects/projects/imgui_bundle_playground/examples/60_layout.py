"""# Layout & Docking

Demonstrates resizable panels and docking using Dear ImGui Bundle.

- `begin_child` with `resize_x` / `resize_y` for resizable layouts
- Docking support via Hello ImGui

**Links:**
- [Docking documentation](https://pthom.github.io/imgui_bundle/)
"""
# TODO: create simplified layout/docking demo
from imgui_bundle import imgui, immapp

def gui():
    imgui.text("TODO: Layout & Docking demo")

immapp.run(gui, window_title="Layout & Docking")
