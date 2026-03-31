"""# ImPlot3D: Butterfly Effect

The Lorenz attractor visualized with [ImPlot3D](https://github.com/brenocq/implot3d). Two trajectories diverge from a tiny initial difference, illustrating chaos theory.

**Links:**
- [ImPlot3D repository](https://github.com/brenocq/implot3d)
- [ImPlot3D in the Explorer](https://traineq.org/imgui_bundle_explorer/?lib=implot3d)
"""
# TODO: adapt from haiku_butterfly.py (replace sliders with knobs)
from imgui_bundle import imgui, immapp

def gui():
    imgui.text("TODO: ImPlot3D butterfly demo")

immapp.run(gui, window_title="ImPlot3D: Butterfly Effect")
