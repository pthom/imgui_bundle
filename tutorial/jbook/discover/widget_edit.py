from imgui_bundle import imgui, hello_imgui, ImVec2


class AppState:
    globe_size: float = 100.0


def gui(app_state: AppState):
    hello_imgui.image_from_asset("images/world.png", ImVec2(app_state.globe_size, 0))
    _changed, app_state.globe_size = imgui.slider_float("Globe size", app_state.globe_size, 20.0, 200.0)


def main():
    app_state = AppState()
    hello_imgui.run(lambda: gui(app_state), window_title="Edit Values", window_size=(220, 220))


if __name__ == "__main__":
    main()
