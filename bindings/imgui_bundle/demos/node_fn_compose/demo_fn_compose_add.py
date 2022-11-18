from __future__ import annotations

from imgui_bundle import imgui_node_editor as imgui_node_editor, run
from imgui_bundle.demos.node_fn_compose.node_fn_compose import *


class IntWithGui(AnyDataWithGui):
    value: int

    def __init__(self, value: int):
        self.value = value

    def gui_data(self, draw_thumbnail: bool = False) -> None:
        imgui.text(f"Int Value={self.value}")


class AddWithGui(FunctionWithGui):
    what_to_add: int

    def __init__(self):
        self.what_to_add = 1

    def f(self, x: IntWithGui) -> IntWithGui:
        return IntWithGui(x.value + self.what_to_add)

    def name(self):
        return "Add"

    def gui_params(self) -> bool:
        imgui.set_next_item_width(100)
        changed, self.what_to_add = imgui.slider_int("##What to add", self.what_to_add, 0, 10)
        return changed


def main():
    functions = [AddWithGui(), AddWithGui(), AddWithGui()]
    nodes = FunctionCompositionNodes(functions)

    x = IntWithGui(1)

    def gui():
        nonlocal x
        _, x.value = imgui.slider_int("X", x.value, 0, 10)
        if imgui.button("Apply"):
            nodes.set_input(x)

        ed.begin("AAA")
        nodes.draw()
        ed.end()

    config_node = imgui_node_editor.Config()
    config_node.settings_file = "demo_fn_compose_add.json"
    run(gui, with_node_editor_config=config_node, window_size=(800, 600), window_title="Functions composition")


if __name__ == "__main__":
    main()
