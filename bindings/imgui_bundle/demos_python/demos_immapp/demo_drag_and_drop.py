"""
Drag and drop: copy, move or swap names between buttons.

Drag a name onto another button to copy it, move it, or swap the two: the radio buttons pick the mode. Each button is
both a drag source and a drop target. Adapted from the drag and drop section of the [Dear ImGui
demo](https://github.com/ocornut/imgui/blob/master/imgui_demo.cpp).

## Python and C++

In C++, `ImGui::SetDragDropPayload` can carry any object (a copy of its bytes). Python can't do that:
`imgui.set_drag_drop_payload_py_id` and `imgui.accept_drag_drop_payload_py_id` carry an integer id, and you keep the
data it refers to elsewhere (here, the index of a name in a list).
"""

import enum
from typing import List
from imgui_bundle import imgui, immapp


class DragMode(enum.Enum):
    Copy = enum.auto()
    Move = enum.auto()
    Swap = enum.auto()


class DemoState:
    mode: DragMode
    names: List[str]

    def __init__(self):
        self.mode = DragMode.Copy
        self.names = [
            "Bobby",
            "Beatrice",
            "Betty",
            "Brianna",
            "Barry",
            "Bernard",
            "Bibi",
            "Blaine",
            "Bryn",
        ]


def gui_drag_and_drop(state: DemoState) -> None:
    if imgui.radio_button("Copy", state.mode == DragMode.Copy):
        state.mode = DragMode.Copy
    imgui.same_line()
    if imgui.radio_button("Move", state.mode == DragMode.Move):
        state.mode = DragMode.Move
    imgui.same_line()
    if imgui.radio_button("Swap", state.mode == DragMode.Swap):
        state.mode = DragMode.Swap

    for n in range(len(state.names)):
        imgui.push_id(n)
        if n % 3 != 0:
            imgui.same_line()
        imgui.button(state.names[n], immapp.em_to_vec2(5.0, 5.0))

        # Our buttons are both drag sources and drag targets here!
        if imgui.begin_drag_drop_source(imgui.DragDropFlags_.none):
            # Set payload to carry the index of our item (in python, the payload is an int)
            drag_data_id = n
            imgui.set_drag_drop_payload_py_id("DND_DEMO_CELL", drag_data_id)

            # Display preview (could be anything, e.g. when dragging an image we could decide to display
            # the filename and a small preview of the image, etc.)
            if state.mode == DragMode.Copy:
                imgui.text(f"Copy {state.names[n]}")
            elif state.mode == DragMode.Move:
                imgui.text(f"Move {state.names[n]}")
            elif state.mode == DragMode.Swap:
                imgui.text(f"Swap {state.names[n]}")
            imgui.end_drag_drop_source()

        if imgui.begin_drag_drop_target():
            payload = imgui.accept_drag_drop_payload_py_id("DND_DEMO_CELL")
            if payload is not None:
                payload_n = payload.data_id
                if state.mode == DragMode.Copy:
                    state.names[n] = state.names[payload_n]
                elif state.mode == DragMode.Move:
                    state.names[n] = state.names[payload_n]
                    state.names[payload_n] = ""
                elif state.mode == DragMode.Swap:
                    state.names[n], state.names[payload_n] = (
                        state.names[payload_n],
                        state.names[n],
                    )
            imgui.end_drag_drop_target()
        imgui.pop_id()


def main() -> None:
    state = DemoState()

    def gui():
        gui_drag_and_drop(state)

    immapp.run(gui)


if __name__ == "__main__":
    main()
