from __future__ import annotations
from typing import Any
from typing import Optional

from imgui_bundle.demos.demo_composition_graph.functions_composition_graph import AnyDataWithGui
from imgui_bundle import imgui


class IntWithGui(AnyDataWithGui):
    value: int = 0

    def gui_data(self, function_name: str) -> None:
        imgui.text(f"Int Value={self.value}")

    def gui_set_input(self) -> Optional[int]:
        imgui.set_next_item_width(100)
        changed, new_value = imgui.slider_int("", self.value, 0, 1000)
        if changed:
            return new_value
        else:
            return None

    def get(self) -> Optional[Any]:
        return self.value

    def set(self, v: Any):
        assert type(v) == int
        self.value = v
