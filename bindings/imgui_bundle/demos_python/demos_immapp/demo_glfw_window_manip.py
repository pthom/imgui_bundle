"""Demonstrates how to manipulate the native GLFW window created by HelloImGui.

`glfw_utils.glfw_window_hello_imgui()` returns the main GLFW window used by HelloImGui.
With this handle you can call any `glfw.*` function to control the native window.

Remember to import imgui_bundle before importing glfw (imgui_bundle comes with its own glfw dll,
which is compatible with python glfw, but it needs to be selected first).
"""

from imgui_bundle import hello_imgui, imgui, glfw_utils
import glfw  # pip install glfw


class AppState:
    opacity: float = 1.0
    request_attention_time : float | None = None


app_state = AppState()


def gui():
    win = glfw_utils.glfw_window_hello_imgui()  # the main GLFW window used by HelloImGui

    imgui.separator_text("Manipulate the native GLFW window:")

    # 1. Maximize / Restore / Iconify
    if imgui.button("Maximize"):
        glfw.maximize_window(win)
    imgui.same_line()
    if imgui.button("Restore"):
        glfw.restore_window(win)
    imgui.same_line()
    if imgui.button("Iconify (minimize)"):
        glfw.iconify_window(win)
    imgui.same_line()
    if imgui.button("Center on monitor"):
        mx, my, mw, mh = glfw.get_monitor_workarea(glfw.get_primary_monitor())
        ww, wh = glfw.get_window_size(win)
        glfw.set_window_pos(win, mx + (mw - ww) // 2, my + (mh - wh) // 2)

    # 2. Window opacity
    opacity_changed, app_state.opacity = imgui.slider_float("Window opacity", app_state.opacity, 0.2, 1.0)
    if opacity_changed:
        glfw.set_window_opacity(win, app_state.opacity)

    # 3. Request attention (flash the taskbar / dock icon).
    imgui.separator_text("Request attention")
    imgui.text("Tip: click on request attention, then switch to another window.")
    imgui.text("This window should flash in the taskbar (or in the dock) after about 3 seconds")
    if imgui.button("Request attention"):
        app_state.request_attention_time = imgui.get_time() + 3
    if app_state.request_attention_time and imgui.get_time() > app_state.request_attention_time:
        glfw.request_window_attention(win)
        app_state.request_attention_time = None


def main():
    glfw.init()  # needed by glfw_utils.glfw_window_hello_imgui
    hello_imgui.run(gui, window_title="GLFW window manipulation")


if __name__ == "__main__":
    main()
