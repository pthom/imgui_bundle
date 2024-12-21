from imgui_bundle import imgui, hello_imgui

class AppState:                                               # 1.
    counter: int = 0                                          # 2.

def gui(app_state: AppState):                                 # 3.
    imgui.text(f"Counter: {app_state.counter}")
    if imgui.button("Increment"):                             # 4.
        app_state.counter += 1
    imgui.set_item_tooltip("Click to increment the counter")  # 5.

    if imgui.button("Exit"):
        hello_imgui.get_runner_params().app_shall_exit = True # 6.

def main():                                                   # 7.
    app_state = AppState()                                    # 7.
    gui_fn = lambda: gui(app_state)                           # 8.
    hello_imgui.run(gui_fn, window_size_auto=True)            # 9.

if __name__ == "__main__":                                    # 7.
    main()                                                    # 7.
