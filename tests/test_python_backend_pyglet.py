"""The pure-Python pyglet backend's mouse events, without a window: a drag forwards the position only (pyglet gives it
the mask of the held buttons, already pressed), a press and a release reach Dear ImGui"""

from typing import Any, Iterator, List, Tuple

import pytest

from imgui_bundle import imgui

pyglet_backend = pytest.importorskip("imgui_bundle.python_backends.pyglet_backend")
mouse = pytest.importorskip("pyglet.window.mouse")


class RecordingIo:
    """Stands for imgui's io: records the mouse events the backend sends"""

    def __init__(self) -> None:
        self.display_size = imgui.ImVec2(800, 600)
        self.buttons: List[Tuple[int, bool]] = []
        self.positions: List[Tuple[float, float]] = []

    def add_mouse_button_event(self, button: int, down: bool) -> None:
        self.buttons.append((button, down))

    def add_mouse_pos_event(self, x: float, y: float) -> None:
        self.positions.append((x, y))


@pytest.fixture
def backend() -> Iterator[Any]:
    context = imgui.create_context()
    mixin = pyglet_backend.PygletMixin()
    mixin.io = RecordingIo()
    yield mixin
    imgui.destroy_context(context)


def test_drag_sends_the_position_only(backend: Any) -> None:
    backend.on_mouse_drag(10, 20, 1, 1, mouse.LEFT | mouse.RIGHT, 0)
    assert backend.io.buttons == []
    assert backend.io.positions == [(10, 600 - 20)]


def test_press_and_release(backend: Any) -> None:
    backend.on_mouse_press(10, 20, mouse.RIGHT, 0)
    backend.on_mouse_release(10, 20, mouse.RIGHT, 0)
    backend.on_mouse_press(10, 20, mouse.MOUSE4, 0)  # a side button: no Dear ImGui button
    assert backend.io.buttons == [(1, True), (1, False)]
