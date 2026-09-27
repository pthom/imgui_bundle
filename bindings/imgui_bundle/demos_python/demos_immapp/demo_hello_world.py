"""
Hello world: a complete app in two lines of code.

[ImmApp](https://imgui-bundle.pages.dev/doc/core-libs/hello-imgui-immapp/) opens the window, runs the loop, and calls
your GUI function at every frame: `immapp.run(gui)` is all it takes. Add widgets to that function, and you have an
app. The C++ version is three lines.
"""

from imgui_bundle import imgui, immapp
immapp.run(lambda: imgui.text("Start your app in 2 lines!"))
