from imgui_bundle.demos.demo_composition_graph.functions_composition_graph import AnyDataWithGui
from imgui_bundle import imgui


class IntWithGui(AnyDataWithGui):
    value: int

    def __init__(self, value: int):
        self.value = value

    def gui_data(self, function_name: str) -> None:
        imgui.text(f"{function_name}")
        imgui.text(f"Int Value={self.value}")

