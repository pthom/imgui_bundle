"""
* [Minimal HTML example](https://traineq.org/imgui_bundle_online/projects/min_bundle_pyodide_app/demo_heart.html): full app in 80 lines, [Source](https://traineq.org/imgui_bundle_online/projects/min_bundle_pyodide_app/demo_heart.source.txt)
"""
from imgui_bundle import imgui, immapp

def gui():
    imgui.text("TODO: Minimal HTML example")

immapp.run(gui, window_title="Minimal HTML example")
