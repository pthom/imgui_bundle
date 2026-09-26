import imgui_bundle.imgui
from imgui_bundle import immapp, implot, hello_imgui
from imgui_bundle.immapp.runnable_code_cell import show_runnable_code_cell
from typing import Any
from numpy.typing import NDArray


def plot_renderer(array: NDArray[Any]) -> None:
    if implot.begin_plot("My Plot", hello_imgui.em_to_vec2(20, 10)):
        implot.plot_line("My Line", array)
        implot.end_plot()


def approx_pi(n: int) -> float:
    return 4 * sum((-1) ** k / (2 * k + 1) for k in range(n))  # type: ignore


def sandbox_code_cell():
    def gui():
        if imgui_bundle.imgui.collapsing_header("Basics"):
            show_runnable_code_cell("A user-editable code cell")

            show_runnable_code_cell(
                "Code Cell that returns a result",
                """
                x = 5
                x
                """)

            show_runnable_code_cell(
                "Code Cell that returns no result",
                """
                x = 5
                """)

            show_runnable_code_cell(
                "Code Cell with a syntax error",
                """
                def square(x)     # missing colon
                    return x * x
                square(5)
                """)

            show_runnable_code_cell(
                "Code Cell that performs a calculation",
                """
                def square(x):
                    return x * x
                square(5)
                """)

        if imgui_bundle.imgui.collapsing_header("Advanced", imgui_bundle.imgui.TreeNodeFlags_.default_open):
            show_runnable_code_cell(
                label_id="Define a time array",
                code="""
                import numpy as np
                t = np.linspace(0, 2*np.pi, 100)
                """)

            show_runnable_code_cell(
                label_id="Code Cell with a custom renderer (plot) (reuse previous variable)",
                code="""
                np.cos(t)
                """,
                result_renderer=plot_renderer)

            show_runnable_code_cell(
                "Code Cell whose result is a live GUI",
                """
                from imgui_bundle import imgui, implot, em_to_vec2
                import numpy as np
                freq = 1.0
                def gui():
                    global freq
                    _, freq = imgui.slider_float("freq", freq, 0.5, 5.0)
                    if implot.begin_plot("Live plot", em_to_vec2(20, 10)):
                        x = np.linspace(0, 2 * np.pi, 200)
                        implot.plot_line("sin", np.sin(freq * x))
                        implot.end_plot()
                gui
                """)

    immapp.run(gui, with_markdown=True, with_implot=True, window_size=(800, 1000))


if __name__ == "__main__":
    sandbox_code_cell()
