import numpy as np
from imgui_bundle import hello_imgui, imgui, implot


text = "Hello"
value = 42

xs = np.array((1.0, 2.0, 3.0, 4.0))
ys = np.array((5.0, 6.0, 7.0, 8.0))


def my_gui(params: hello_imgui.RunnerParams):
    global text, value
    imgui.text("Hello")
    imgui.button("Click")
    changed, text = imgui.input_text("Enter text", text)
    _, value = imgui.slider_int("Value", value, 0, 100)
    if imgui.button("Exit"):
        params.app_shall_exit = True
    implot.show_demo_window()

    implot.begin_plot("My Plot")
    implot.plot_bars("Bars", xs, ys, 3.0)
    implot.end_plot()


params = hello_imgui.RunnerParams()


def gui_with_params():
    my_gui(params)


implot.create_context()
params.callbacks.show_gui = gui_with_params

hello_imgui.run(params)
