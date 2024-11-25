from imgui_bundle import imgui, hello_imgui

NAME = "John"


def gui():
    global NAME
    _, NAME = imgui.input_text("Name", NAME)


hello_imgui.run(gui)
