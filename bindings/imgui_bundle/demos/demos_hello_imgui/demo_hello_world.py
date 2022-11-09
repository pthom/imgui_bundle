from imgui_bundle import imgui, ImVec2, run


def gui():
    imgui.text("Hello, world!")


run(
    # The Gui function to run
    gui_function=gui,
    # the window title
    window_title="Hello!",

    # If no size is passed, the window size will be computed automatically!
    # window_size=(200, 200),

    # Uncomment this to restore window position and size from previous run
    # restore_previous_geometry=True
)
