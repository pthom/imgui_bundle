# port of bindings/imgui_bundle/demos_cpp/demos_nanovg/demo_nanovg_full.cpp
from imgui_bundle import imgui, nanovg as nvg, hello_imgui, ImVec2, ImVec4
from imgui_bundle.demos_python import demo_utils
from imgui_bundle.demos_python.demos_nanovg.demo_nanovg_full import demo_nanovg_full_impl
from typing import List


nvg_imgui = nvg.nvg_imgui


class MyNvgDemo:
    blowup: bool
    nvgDemoData: demo_nanovg_full_impl.DemoData
    vg: nvg.Context

    def init(self, vg: nvg.Context):
        self.vg = vg
        self.blowup = False

        self.nvgDemoData = demo_nanovg_full_impl.DemoData()
        status = demo_nanovg_full_impl.load_demo_data(vg, self.nvgDemoData)
        if status != 0:
            print("Could not load demo data.")
            return

    def reset(self):
        demo_nanovg_full_impl.free_demo_data(self.vg, self.nvgDemoData)

    def render(self, width: float, height: float, mouse_x: float, mouse_y: float, t: float):
        demo_nanovg_full_impl.render_demo(self.vg, mouse_x, mouse_y, width, height, t, self.blowup, self.nvgDemoData)


class AppState:
    myNvgDemo: MyNvgDemo
    vg: nvg.Context
    myFrameBuffer: nvg_imgui.NvgFramebuffer
    clear_color: List[float]
    display_in_frame_buffer: bool = False

    def __init__(self):
        self.clear_color = [0.3, 0.3, 0.32, 1.0]


def main():
    # This call is specific to the ImGui Bundle interactive manual. In a standard application, you could write:
    #         hello_imgui.set_assets_folder("my_assets")  # (By default, HelloImGui will search inside "assets")
    demo_utils.set_hello_imgui_demo_assets_folder()

    app_state = AppState()

    runner_params = hello_imgui.RunnerParams()
    runner_params.imgui_window_params.default_imgui_window_type = hello_imgui.DefaultImGuiWindowType.no_default_window
    runner_params.app_window_params.window_geometry.size = (1200, 900)

    def post_init():
        app_state.vg = nvg_imgui.create_nvg_context_hello_imgui(nvg_imgui.NvgCreateFlags.antialias.value | nvg_imgui.NvgCreateFlags.stencil_strokes.value)
        app_state.myNvgDemo = MyNvgDemo()
        app_state.myNvgDemo.init(app_state.vg)
        nvg_image_flags = 0
        app_state.myFrameBuffer = nvg_imgui.NvgFramebuffer(app_state.vg, 1000, 600, nvg_image_flags)

    def before_exit():
        app_state.myNvgDemo.reset()
        app_state.myFrameBuffer = None
        nvg_imgui.delete_nvg_context_hello_imgui(app_state.vg)

    runner_params.callbacks.enqueue_post_init(post_init)
    runner_params.callbacks.enqueue_before_exit(before_exit)

    def nvg_drawing_function(_: nvg.Context, width: float, height: float):
        now = imgui.get_time()
        mouse_pos = ImVec2(
            imgui.get_mouse_pos().x - imgui.get_main_viewport().pos.x,
            imgui.get_mouse_pos().y - imgui.get_main_viewport().pos.y)
        app_state.myNvgDemo.render(width, height, mouse_pos.x, mouse_pos.y, now)

    def custom_background():
        clear_color_vec4 = ImVec4(*app_state.clear_color)
        nvg_imgui.render_nvg_to_background(app_state.vg, nvg_drawing_function, clear_color_vec4)

    runner_params.callbacks.custom_background = custom_background

    def gui():
        imgui.set_next_window_pos(ImVec2(0, 0), imgui.Cond_.appearing.value)
        imgui.begin("My Window!", None, imgui.WindowFlags_.always_auto_resize.value)

        if app_state.display_in_frame_buffer:
            clear_color_vec4 = ImVec4(*app_state.clear_color)
            nvg_imgui.render_nvg_to_frame_buffer(app_state.vg, app_state.myFrameBuffer, nvg_drawing_function, clear_color_vec4)
            imgui.image(app_state.myFrameBuffer.texture_id, ImVec2(1000, 600))

        imgui.button("?##Note")
        if imgui.is_item_hovered():
            imgui.set_tooltip("This is the complete NanoVG demo, ported to ImGui Bundle (C++ and Python)\n"
                               "It displays fake widgets, as a way to display NanoVG drawing capabilities.\n"
                               "However, those widgets are not interactive.\n")

        _, app_state.myNvgDemo.blowup = imgui.checkbox("Blowup", app_state.myNvgDemo.blowup)
        if imgui.is_item_hovered():
            imgui.set_tooltip("When checked, apply a simple transform to the drawing")

        _, app_state.display_in_frame_buffer = imgui.checkbox("Display in framebuffer", app_state.display_in_frame_buffer)
        if imgui.is_item_hovered():
            imgui.set_tooltip("When checked, the drawing is also rendered to a framebuffer, and displayed as a texture.")

        imgui.set_next_item_width(hello_imgui.em_size(15))
        _, app_state.clear_color = imgui.color_edit4("Clear Color", app_state.clear_color)
        if imgui.is_item_hovered():
            imgui.set_tooltip("Background color of the drawing")

        imgui.end()

    runner_params.callbacks.show_gui = gui

    runner_params.fps_idling.enable_idling = False

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
