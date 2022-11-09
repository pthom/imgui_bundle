from imgui_bundle import imgui, ImVec2, run


def gui():
    imgui.text("Hello, world!")


run(gui_function=gui, window_size=ImVec2(200, 50), window_title="Hello!")
