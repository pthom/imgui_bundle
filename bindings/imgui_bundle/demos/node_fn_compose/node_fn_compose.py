from __future__ import annotations
from imgui_bundle import imgui, imgui_node_editor as ed, icons_fontawesome, ImVec2

from typing import List, Optional
from abc import ABC, abstractmethod


# transform a list into a list of adjacent pairs
# For example : [a, b, c] -> [ [a, b], [b, c]]
def overlapping_pairs(iterable):
    it = iter(iterable)
    a = next(it, None)

    for b in it:
        yield (a, b)
        a = b


# transform a list into a circular list of adjacent pairs
# For example : [a, b, c] -> [ [a, b], [b, c], [c, a]]
def overlapping_pairs_cyclic(iterable):
    it = iter(iterable)
    a = next(it, None)
    first = a
    for b in it:
        yield (a, b)
        a = b
    last = a
    yield (last, first)


class AnyDataWithGui(ABC):
    """
    Override this class with your types, and implement a draw function that presents it content
    """
    @abstractmethod
    def gui_data(self, draw_thumbnail: bool = False) -> None:
        pass


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
        return x


class _FunctionNode:
    function: Optional[FunctionWithGui]
    next_function: Optional[_FunctionNode]
    input_data: Optional[AnyDataWithGui]
    output_data: Optional[AnyDataWithGui]

    node_id: ed.NodeId
    pin_input: ed.PinId
    pin_output: ed.PinId
    link_id: ed.LinkId

    def __init__(self, function: FunctionWithGui, next_function: Optional[FunctionWithGui] = None) -> None:
        self.function = function
        self.next_function = next_function
        self.input_data = None
        self.output_data = None

        self.node_id = ed.NodeId.create()
        self.pin_input = ed.PinId.create()
        self.pin_output = ed.PinId.create()
        self.link_id = ed.LinkId.create()

    def draw_node(self, draw_input: bool, draw_output: bool, idx: int) -> None:
        ed.begin_node(self.node_id)
        position = ed.get_node_position(self.node_id)
        if position.x == 0 and position.y == 0:
            width_between_nodes = 200
            ed.set_node_position(self.node_id, ImVec2(idx * width_between_nodes + 1, 0) )

        imgui.text(self.function.name())

        id_fn = str(id(self.function))
        imgui.push_id(id_fn)

        params_changed= self.function.gui_params()
        if params_changed:
            if self.input_data is not None and self.function is not None:
                self.output_data = self.function.f(self.input_data)
                if self.next_function is not None:
                    self.next_function.set_input(self.output_data)
        imgui.pop_id()

        if draw_input:
            ed.begin_pin(self.pin_input, ed.PinKind.input)
            imgui.text(icons_fontawesome.ICON_FA_CIRCLE)
            ed.end_pin()

        if draw_output:
            if self.output_data is None:
                imgui.text("None")
            else:
                self.output_data.gui_data(draw_thumbnail=True)
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
            self.output_data = self.function.f(input_data)
            if self.next_function is not None:
                self.next_function.set_input(self.output_data)


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
            draw_output = True
            fn.draw_node(draw_input=draw_input, draw_output=draw_output, idx=i)
        for i, fn in enumerate(self.function_nodes):
            fn.draw_link()
