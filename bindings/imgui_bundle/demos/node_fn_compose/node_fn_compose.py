from __future__ import annotations
from imgui_bundle import run, imgui, imgui_node_editor as ed, icons_fontawesome
from imgui_bundle.demos.node_fn_compose.functional_utils import overlapping_pairs

from typing import Callable, Any, List, Optional
from abc import ABC, abstractmethod


class AnyDataWithGui:
    """
    Override this class with your types, and implement a draw function that presents it content
    """

    def gui_data(self, draw_thumbnail: bool = False) -> None:
        imgui.text("draw\nnot implemented")


class FunctionWithGui(ABC):
    @abstractmethod
    def f(self, x: AnyDataWithGui) -> AnyDataWithGui:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    def gui_params(self) -> bool:
        """override this if you want to provide a gui for the function inner params
        (i.e neither input nor output params, but the function internal state)
        It should return True if the inner params were changed.
        """
        pass


class _InputWithGui(FunctionWithGui):
    def __init__(self) -> None:
        pass

    def name(self):
        return "Input"

    def f(self, x: AnyDataWithGui):
        return x


class _OutputWithGui(FunctionWithGui):
    def __init__(self) -> None:
        pass

    def name(self):
        return "Output"

    def f(self, x: AnyDataWithGui):
        return None


class _FunctionNode:
    function: Optional[FunctionWithGui]
    next_function: Optional[_FunctionNode]
    input_data: Optional[AnyDataWithGui]

    node_id: ed.NodeId
    pin_input: ed.PinId
    pin_output: ed.PinId
    link_id: ed.LinkId

    def __init__(self, function: FunctionWithGui, next_function: Optional[FunctionWithGui] = None) -> None:
        self.function = function
        self.next_function = next_function
        self.input_data = None

        self.node_id = ed.NodeId.create()
        self.pin_input = ed.PinId.create()
        self.pin_output = ed.PinId.create()
        self.link_id = ed.LinkId.create()

    def draw_node(self, draw_input: bool = True, draw_output: bool = True) -> None:
        ed.begin_node(self.node_id)

        imgui.text(self.function.name())

        id_fn = str(id(self.function))
        imgui.push_id(id_fn)
        if self.function.gui_params():
            if self.input_data is not None and self.function is not None and self.next_function is not None:
                output = self.function.f(self.input_data)
                self.next_function.set_input(output)
        imgui.pop_id()

        if draw_input:
            ed.begin_pin(self.pin_input, ed.PinKind.input)
            imgui.text(icons_fontawesome.ICON_FA_CIRCLE)
            ed.end_pin()
            if self.input_data is None:
                imgui.text("None")
            else:
                self.input_data.gui_data(draw_thumbnail=True)

        if draw_output:
            imgui.text(" " * 30)
            imgui.same_line()
            ed.begin_pin(self.pin_output, ed.PinKind.output)
            imgui.text(icons_fontawesome.ICON_FA_CIRCLE)
            ed.end_pin()

        ed.end_node()

    def draw_link(self) -> None:
        if self.next_function is None:
            return
        ed.link(self.link_id, self.pin_output, self.next_function.pin_input)

    def set_input(self, input_data: AnyDataWithGui) -> None:
        self.input_data = input_data
        if self.function is not None:
            output = self.function.f(input_data)
            if self.next_function is not None:
                self.next_function.set_input(output)


class FunctionCompositionNodes:
    function_nodes: List[_FunctionNode]

    def __init__(self, functions: List[FunctionWithGui]) -> None:
        input_fake_function = _InputWithGui()
        output_fake_function = _OutputWithGui()

        self.function_nodes = []
        self.function_nodes.append(_FunctionNode(input_fake_function))
        for f in functions:
            function_node = _FunctionNode(f)
            self.function_nodes.append(function_node)
        self.function_nodes.append(_FunctionNode(output_fake_function))

        for f1, f2 in overlapping_pairs(self.function_nodes):
            f1.next_function = f2

    def set_input(self, input_data: AnyDataWithGui) -> None:
        self.function_nodes[0].set_input(input_data)

    def draw(self) -> None:
        # draw function nodes
        for i, fn in enumerate(self.function_nodes):
            draw_input = i != 0
            draw_output = i != len(self.function_nodes) - 1
            fn.draw_node(draw_input=draw_input, draw_output=draw_output)
        for i, fn in enumerate(self.function_nodes):
            fn.draw_link()


#######################


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


def test():
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

    run(gui, with_node_editor=True, window_size=(800, 600), window_title="Functions composition")


if __name__ == "__main__":
    test()
