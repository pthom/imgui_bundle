from __future__ import annotations
from imgui_bundle import imgui, immapp, hello_imgui


def gui():
    imgui.text("Hello world")
    imgui.text(f"FPS = {hello_imgui.frame_rate()}")


def main():
    runner_params = hello_imgui.RunnerParams()
    runner_params.callbacks.show_gui = gui

    immapp.run(runner_params)


if __name__ == "__main__":
    main()
