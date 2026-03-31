"""# ImmVision: Image Inspection

Interactive image debugging with zoom, pan, pixel inspection, and colormaps using [ImmVision](https://github.com/pthom/immvision).

- Pan and zoom with the mouse
- Inspect pixel values
- Apply colormaps in the options panel
- Linked views: both images zoom together

**Links:**
- [ImmVision repository](https://github.com/pthom/immvision)
"""
# TODO: create - download web images, Sobel filter with opencv
from imgui_bundle import imgui, immapp

def gui():
    imgui.text("TODO: ImmVision demo")

immapp.run(gui, window_title="ImmVision: Image Inspection")
