import io, base64
import flet as ft
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def fourier_square(x, n_terms):
    result = np.zeros_like(x)
    for k in range(1, n_terms + 1):
        n = 2*k - 1
        result += np.sin(n * x) / n
    return (4 / np.pi) * result


def fig_to_data_url(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def main(page: ft.Page):
    page.title = "Fourier — square wave"
    page.padding = 20

    state = {"n_terms": 5, "show_components": False}
    x = np.linspace(-2*np.pi, 2*np.pi, 1000)
    y_true = np.sign(np.sin(x))

    fig, ax = plt.subplots(figsize=(8, 4.5))
    chart_img = ft.Image(expand=True) #, fit=ft.ImageFit.CONTAIN)
    info = ft.Text()

    def redraw():
        n = state["n_terms"]
        ax.clear()
        ax.plot(x, y_true, "k--", alpha=0.5, label="square wave")
        ax.plot(x, fourier_square(x, n), "b-", linewidth=2, label=f"approx, N={n}")
        if state["show_components"]:
            for k in range(1, n + 1):
                m = 2*k - 1
                ax.plot(x, (4/np.pi) * np.sin(m*x)/m, alpha=0.3, linewidth=0.8)
        ax.set_xlabel(r"$x$"); ax.set_ylabel(r"$f(x)$")
        ax.set_ylim(-1.5, 1.5); ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right", framealpha=0.9)

        chart_img.src = fig_to_data_url(fig)
        chart_img.update()

        info.value = f"Using {n} odd harmonic(s): n = 1, 3, …, {2*n - 1}"
        info.update()

    def on_slider_end(e):
        state["n_terms"] = int(e.control.value); redraw()

    def on_toggle(e):
        state["show_components"] = e.control.value; redraw()

    page.add(
        ft.Column([
            ft.Markdown(
                r"""
### Fourier series of a square wave
$$ f(x) = \frac{4}{\pi}\sum_{k=1}^{N}\frac{\sin\big((2k-1)x\big)}{2k-1} $$
""",
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            ),
            ft.Row([
                ft.Text("N:"),
                ft.Slider(min=1, max=30, value=5, divisions=29,
                          label="N = {value}",
                          on_change_end=on_slider_end, expand=True),
            ]),
            ft.Switch(label="Show individual harmonics", on_change=on_toggle),
            info,
            chart_img,
        ], expand=True)
    )
    redraw()


ft.run(main)