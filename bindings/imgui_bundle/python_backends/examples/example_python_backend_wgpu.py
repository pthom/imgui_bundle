# wgpu (see https://github.com/pygfx/wgpu-py and https://wgpu-py.readthedocs.io/en/stable/)
# provides a Python implementation of WebGPU together with
# an easy-to-use interface to Dear ImGui Bundle!
#
# See more examples in the wgpu-py repository here:
#    https://github.com/pygfx/wgpu-py/tree/main/examples
#    (look for examples whose name starts with "imgui_")
#
# Requirements: install wgpu with `pip install wgpu`

import wgpu
import sys
from imgui_bundle import imgui, imgui_ctx
from wgpu.gui.auto import WgpuCanvas, run
from wgpu.utils.imgui import ImguiRenderer


# Create a canvas to render to
canvas = WgpuCanvas(title="imgui", size=(640, 480))

# Create a wgpu device
adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
device = adapter.request_device_sync()

app_state = {"text": "Hello, World\nLorem ipsum, etc.\netc."}
imgui_renderer = ImguiRenderer(device, canvas)


def update_gui():
    imgui.new_frame()
    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("File", True):
            clicked_quit, _ = imgui.menu_item("Quit", "Cmd+Q", False, True)
            if clicked_quit:
                sys.exit(0)

            imgui.end_menu()
        imgui.end_main_menu_bar()

    imgui.show_demo_window()

    imgui.set_next_window_size((300, 0), imgui.Cond_.appearing)
    imgui.set_next_window_pos((0, 20), imgui.Cond_.appearing)

    imgui.begin("Custom window", None)
    imgui.text("Example Text")

    if imgui.button("Hello"):
        print("World")

    _, app_state["text"] = imgui.input_text_multiline(
        "Edit", app_state["text"], imgui.ImVec2(200, 200)
    )
    io = imgui.get_io()
    imgui.text(
        f"""
    Keyboard modifiers:
        {io.key_ctrl=}
        {io.key_alt=}
        {io.key_shift=}
        {io.key_super=}"""
    )

    if imgui.button("Open popup"):
        imgui.open_popup("my popup")
    with imgui_ctx.begin_popup_modal("my popup") as popup:
        if popup.visible:
            imgui.text("Hello from popup!")
            if imgui.button("Close popup"):
                imgui.close_current_popup()

    imgui.end()

    imgui.end_frame()
    imgui.render()

    return imgui.get_draw_data()


# set the GUI update function that gets called to return the draw data
imgui_renderer.set_gui(update_gui)


def draw_frame():
    imgui_renderer.render()
    canvas.request_draw()


if __name__ == "__main__":
    canvas.request_draw(draw_frame)
    run()
