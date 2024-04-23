from __future__ import annotations
from imgui_bundle import imgui, immapp, hello_imgui


def gui():
    imgui.text("Hello world")
    imgui.text(f"FPS = {hello_imgui.frame_rate()}")


def main():
    runner_params = hello_imgui.RunnerParams()
    runner_params.callbacks.show_gui = gui
    runner_params.platform_backend_type = hello_imgui.PlatformBackendType.glfw

    runner_params.renderer_backend_options.open_gl_options = hello_imgui.OpenGlOptions()
    runner_params.renderer_backend_options.open_gl_options.major_version = 3
    runner_params.renderer_backend_options.open_gl_options.minor_version = 2
    runner_params.renderer_backend_options.open_gl_options.glsl_version = "#version 130"
    runner_params.renderer_backend_options.open_gl_options.use_core_profile = True

    immapp.run(runner_params)


if __name__ == "__main__":
    main()
