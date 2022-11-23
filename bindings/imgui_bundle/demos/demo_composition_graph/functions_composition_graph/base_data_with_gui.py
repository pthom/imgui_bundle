from __future__ import annotations
from typing import Optional

from imgui_bundle.demos.demo_composition_graph.functions_composition_graph import AnyDataWithGui
from imgui_bundle import imgui


class IntWithGui(AnyDataWithGui):
    value: int

    def __init__(self, value: int):
        self.value = value

    def gui_data(self, function_name: str) -> None:
        imgui.text(f"Int Value={self.value}")

    def gui_set_input(self) -> Optional[IntWithGui]:
        imgui.set_next_item_width(100)
        changed, new_value = imgui.slider_int("", self.value, 0, 1000)
        if changed:
            return IntWithGui(new_value)
        else:
            return None
