import os
import sys

this_dir = os.path.dirname(__file__)
sys.path.append(f"{this_dir}/../bindings")

from lg_hello_imgui import imgui, implot, hello_imgui


text = "Hello"
value = 42


def my_gui(params: hello_imgui.RunnerParams):
    global text, value
    imgui.text("Hello")
    imgui.button("Click")
    changed, text = imgui.input_text("Enter text", text)
    _, value = imgui.slider_int("Value", value, 0, 100)
    if imgui.button("Exit"):
        params.app_shall_exit = True
    implot.show_demo_window()


params = hello_imgui.RunnerParams()


def gui_with_params():
    my_gui(params)


implot.create_context()
params.callbacks.show_gui = gui_with_params
hello_imgui.override_assets_folder(this_dir)

hello_imgui.run(params)
