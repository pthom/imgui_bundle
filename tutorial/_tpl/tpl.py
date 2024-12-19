from imgui_bundle import imgui, hello_imgui


class AppState:
    pass


def gui(app_state: AppState):
    pass


def main():
    app_state = AppState()
    gui_fn = lambda: gui(app_state)
    hello_imgui.run(gui_fn, window_size_auto=True)


if __name__ == "__main__":
    main()
