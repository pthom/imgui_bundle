"""Hello World example:
Create an App in 3 lines of code,
using Dear ImGui and Hello ImGui!
"""
from imgui_bundle import hello_imgui, imgui

def gui():
    imgui.text("Hello, world!")


# The window title will become the HTML title of the rendered page.
hello_imgui.run(gui, window_title="Hello HelloImGui!")
