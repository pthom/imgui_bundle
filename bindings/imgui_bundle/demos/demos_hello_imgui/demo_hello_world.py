from imgui_bundle import imgui, ImVec2, run


def gui():
    imgui.text("Hello, world!")


run(
    gui_function=gui,  # The Gui function to run
    window_title="Hello!",  # the window title
    window_size_auto=True,  # Auto size the application window given its widgets
    # Uncomment the next line to restore window position and size from previous run
    # window_restore_previous_geometry==True
)
