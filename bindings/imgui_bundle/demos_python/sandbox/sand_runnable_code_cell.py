from imgui_bundle import immapp, implot, hello_imgui
from imgui_bundle.immapp.runnable_code_cell import show_runnable_code_cell
import numpy as np


def plot_renderer(array: np.ndarray) -> None:
    implot.begin_plot("My Plot", hello_imgui.em_to_vec2(20, 10))
    implot.plot_line("My Line", array)
    implot.end_plot()


def approx_pi(n: int) -> float:
    return 4 * sum((-1) ** k / (2 * k + 1) for k in range(n))


def sandbox_code_cell():
    def gui():
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
            "Code Cell that performs a calculation",
            """
            def square(x):
                return x * x
            square(5)
            """)

        show_runnable_code_cell(
            "Code Cell with a syntax error",
            """
            def square(x)     # missing colon
                return x * x
            square(5)
            """)

        # def my_plot_renderer(result: Any) -> None:
        #     imgui.plot_lines("My Plot", result)

        show_runnable_code_cell(
            label_id="Code Cell with a custom renderer (plot)",
            code="""
            import numpy as np
            t = np.linspace(0, 2*np.pi, 100)
            np.sin(t)
            """,
            result_renderer=plot_renderer)


    immapp.run(gui, with_markdown=True, with_implot=True, window_size=(800, 1000))


if __name__ == "__main__":
    sandbox_code_cell()
