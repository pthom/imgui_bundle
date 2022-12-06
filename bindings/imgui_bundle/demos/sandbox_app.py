import imgui_bundle
from imgui_bundle import imgui


def make_gui_closure():
    def gui():
        imgui.text("Hello")
        if imgui.button("text"):
            settings, size = imgui.save_ini_settings_to_memory()

    return gui


def main():
    gui = make_gui_closure()
    imgui_bundle.run(gui, window_size=(1000, 800))


if __name__ == "__main__":
    main()
