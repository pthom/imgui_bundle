"""# Fiatlight: Image Pipeline

[Fiatlight](https://pthom.github.io/fiatlight_doc) turns Python functions into interactive apps with visual pipelines.

This demo shows an image processing pipeline: download an image, apply edge detection, display the result - all as connected nodes.

> *Note: Fiatlight works best on desktop where it can auto-save data and layout.*

**Links:**
- [Fiatlight documentation](https://pthom.github.io/fiatlight_doc)
- [Fiatlight repository](https://github.com/pthom/fiatlight)
"""
# TODO: create - download image, edge detection, display as fiatlight pipeline
from imgui_bundle import imgui, immapp

def gui():
    imgui.text("TODO: Fiatlight image pipeline demo")

immapp.run(gui, window_title="Fiatlight: Image Pipeline")
