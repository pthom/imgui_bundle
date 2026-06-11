"""Demonstrates how to manipulate the glfw window created by HelloImGui.

 glfw_utils.glfw_window_hello_imgui is a function that returns the main glfw window used by HelloImGui
"""

from imgui_bundle import hello_imgui, imgui, glfw_utils
import glfw  # pip install glfw


def gui():
    imgui.text("Hello")
    if imgui.button("maximize window"):
        win = glfw_utils.glfw_window_hello_imgui()  # get the main glfw window used by HelloImGui
        glfw.maximize_window(win)


glfw.init()  # needed by glfw_utils.glfw_window_hello_imgui
hello_imgui.run(gui)
