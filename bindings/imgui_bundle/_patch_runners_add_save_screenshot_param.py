"""Patch the immapp and hello_imgui runners for tutorials.
- Will save a screenshot of the final app state
"""
from typing import Callable

GuiFunction = Callable[[], None]


def _is_in_tutorial() -> bool:
    return True


def _save_hello_imgui_screenshot(image_file: str) -> None:
    from imgui_bundle import hello_imgui
    import cv2
    app_image = hello_imgui.final_app_window_screenshot()
    scale = 1.0 / hello_imgui.final_app_window_screenshot_framebuffer_scale()
    thumbnail = cv2.resize(app_image, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    thumbnail = cv2.cvtColor(thumbnail, cv2.COLOR_RGBA2BGR)
    cv2.imwrite(image_file, thumbnail)


def _get_caller_filename(depth: int):
    import inspect
    stack = inspect.stack()
    caller_frame = stack[depth]
    caller_file = caller_frame.filename
    return caller_file


def patch_runners_add_save_screenshot_param() -> None:
    from imgui_bundle import immapp, hello_imgui

    def patch_runner(run_backup):
        def patched_run(*args, **kwargs):
            caller_file = _get_caller_filename(2)

            run_backup(*args, **kwargs)

            save_screenshot = kwargs.get("save_screenshot", False)
            if "save_screenshot" in kwargs:
                del kwargs["save_screenshot"]
            if "imgui_bundle/tutorial/" in caller_file:
                save_screenshot = True

            if save_screenshot:
                image_file = caller_file.replace(".py", ".jpg")
                _save_hello_imgui_screenshot(image_file)
        return patched_run

    immapp_run_backup = immapp.run
    immapp.run = patch_runner(immapp_run_backup)

    hello_imgui_run_backup = hello_imgui.run
    hello_imgui.run = patch_runner(hello_imgui_run_backup)
