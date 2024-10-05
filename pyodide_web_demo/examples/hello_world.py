# Example 1: Hello World
"""This example demonstrates the basic usage of Dear ImGui by creating a simple "Hello World" window.
"""
from imgui_bundle import hello_imgui, imgui

def gui():
    imgui.text("Hello, world!")


runner_params = hello_imgui.RunnerParams()
runner_params.callbacks.show_gui = gui
hello_imgui.run(runner_params)
