# Demo gradient with ImGuizmo
# See equivalent C++ program: demos_cpp/demos_imguizmo/demo_guizmo_gradient.main.cpp
# Hum... I don't get the point of this widget

from typing import List
from imgui_bundle.demos_python.demo_utils.api_demos import GuiFunction
from imgui_bundle import imgui, ImVec4, ImVec2, imguizmo, immapp


def add_imvec4(a: ImVec4, b: ImVec4) -> ImVec4:
    return ImVec4(a.x + b.x, a.y + b.y, a.z + b.z, a.w + b.w)


def mul_scalar_imvec4(a: ImVec4, k: float) -> ImVec4:
    return ImVec4(a.x * k, a.y * k, a.z * k, a.w * k)


ImVec4.__add__ = add_imvec4  # type: ignore # monkey patching
ImVec4.__mul__ = mul_scalar_imvec4  # type: ignore # monkey patching


class MyGradient(imguizmo.im_gradient.DelegateStl):  # type: ignore
    points: List[ImVec4]

    def __init__(self) -> None:
        imguizmo.im_gradient.DelegateStl.__init__(self)
        # The last value (ImVec4.w) stores the position on a line
        nb_elems = 4.0
        pos = 0.0
        dpos = 1.0 / (nb_elems - 1.0)
        self.points = []
        self.points.append(ImVec4(1, 1, 1, pos))
        pos += dpos
        self.points.append(ImVec4(0, 1, 1, pos))
        pos += dpos
        self.points.append(ImVec4(1, 0, 1, pos))
        pos += dpos
        self.points.append(ImVec4(1, 1, 0, pos))
        pos += dpos

    def get_points_list(self) -> List[ImVec4]:
        return self.points

    def edit_point(
        self, point_index: int, value: ImVec4
    ) -> int:  # overridable (pure virtual)
        self.points[point_index] = value
        return 0

    def get_point(self, t: float) -> ImVec4:
        sorted_values = self.sorted_values()
        if t <= 0.0:
            return sorted_values[0]
        elif t >= 1.0:
            return sorted_values[-1]

        idx = len(sorted_values) - 1
        while (idx >= 1) and (t < sorted_values[idx].w):
            idx -= 1

        v0 = sorted_values[idx]
        v1 = sorted_values[idx + 1]
        interval_length = v1.w - v0.w
        k0 = (t - v0.w) / interval_length
        k1 = 1.0 - k0
        r = v0 * k0 + v1 * k1  # type: ignore
        return r  # type: ignore

    def add_point(self, value: ImVec4) -> None:
        self.points.append(value)

    def sorted_values(self) -> List[ImVec4]:
        r = sorted(self.points, key=lambda p: p.w)
        return r


# This returns a closure function that will later be invoked to run the app
def make_closure_demo_guizmo_gradient() -> GuiFunction:
    my_gradient = MyGradient()
    size = ImVec2(400, 20)

    def gui() -> None:
        _result = imguizmo.im_gradient.edit_pure(my_gradient, size)
        imgui.text_wrapped(
            """
            I'm not sure about the purpose of this widget.
            You can drag squares, and double click to add some more
        """
        )

    return gui


def main():
    gui = make_closure_demo_guizmo_gradient()

    # Run app
    immapp.run(gui, window_size=(400, 100))


if __name__ == "__main__":
    main()
