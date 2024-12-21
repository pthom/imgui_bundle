from imgui_bundle import imgui, hello_imgui


def gui():                                                                  # 1.
    imgui.text("Hello, World!")                                             # 2.


hello_imgui.run(gui, window_title="Hello, World!", window_size_auto=True)   # 3.
