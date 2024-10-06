# Example 1: Hello World
"""This example demonstrates the basic usage of Dear ImGui by creating a simple "Hello World" window.
"""
from imgui_bundle import hello_imgui, imgui

def gui():
    imgui.text("Hello, world!")


# The window title will become the HTML title of the rendered page.
hello_imgui.run(gui, window_title="Hello HelloImGui!")
