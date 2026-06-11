# pip install imgui-bundle numpy
import numpy as np
from imgui_bundle import imgui, implot, immapp, imgui_md


# Plain Python state — no callbacks, no widget objects
state = {"n_terms": 5, "show_components": False}

# x is constant; y_true is constant. Compute once.
x      = np.linspace(-2*np.pi, 2*np.pi, 1000)
y_true = np.sign(np.sin(x))


def fourier_square(x, n_terms):
    result = np.zeros_like(x)
    for k in range(1, n_terms + 1):
        n = 2*k - 1
        result += np.sin(n * x) / n
    return (4 / np.pi) * result


def gui():
    imgui_md.render(r"""
### Fourier series of a square wave
$$ f(x) = \frac{4}{\pi}\sum_{k=1}^{N}\frac{\sin((2k-1)x)}{2k-1} $$
Adjust $N$ to add more harmonics.
""")

    # These calls *both* draw the widget AND return its updated value
    _, state["n_terms"]         = imgui.slider_int("N", state["n_terms"], 1, 30)
    _, state["show_components"] = imgui.checkbox(
        "Show individual harmonics", state["show_components"])

    n = state["n_terms"]
    imgui.text(f"Using {n} odd harmonic(s): n = 1, 3, ..., {2*n - 1}")

    # Recomputed every frame — fast enough at this size, GPU-rendered plot
    y_approx = fourier_square(x, n)

    if implot.begin_plot("Square wave approximation", size=(-1, 400)):
        implot.setup_axes("x", "f(x)")
        implot.setup_axes_limits(-2*np.pi, 2*np.pi, -1.5, 1.5,
                                 cond=implot.Cond_.once.value)
        implot.plot_line("square wave", x, y_true)
        implot.plot_line(f"approx N={n}", x, y_approx)

        if state["show_components"]:
            for k in range(1, n + 1):
                m = 2*k - 1
                implot.plot_line(f"harmonic {m}",
                                 x, (4/np.pi) * np.sin(m*x) / m)

        implot.end_plot()


immapp.run(
    gui_function=gui,
    window_title="Fourier — square wave",
    window_size=(900, 700),
    with_implot=True,
    with_markdown=True,
    with_latex=True
)