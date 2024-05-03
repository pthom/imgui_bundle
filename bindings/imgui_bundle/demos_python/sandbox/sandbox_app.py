from __future__ import annotations
from imgui_bundle import imgui, immapp, hello_imgui
import time

start = time.time()


def gui():
    imgui.text("Hello world")
    imgui.text(f"FPS = {hello_imgui.frame_rate()}")
    remaining = 5 - (time.time() - start)
    imgui.text(f"Remaining = {remaining:.2f} sec")
    now = time.time()
    if (now - start) > 5:
        hello_imgui.get_runner_params().app_shall_exit = True


def main():
    runner_params = hello_imgui.RunnerParams()

    # Demo / how to use null backend
    # runner_params.platform_backend_type = hello_imgui.PlatformBackendType.null
    # runner_params.renderer_backend_type = hello_imgui.RendererBackendType.null

    runner_params.callbacks.show_gui = gui
    immapp.run(runner_params)


if __name__ == "__main__":
    main()
