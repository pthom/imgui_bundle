# Adaptation of imgui_bundle/demos_cpp/demos_nanovg/demo_nanovg_heart.cpp

from imgui_bundle import hello_imgui, imgui, nanovg as nvg, ImVec2
import math

nvg_imgui = nvg.nvg_imgui


def draw_heart(vg: nvg.Context, center: ImVec2, size: float, t: float):
    x = center.x
    y = center.y
    scale = math.sin(t * 10) * 0.1 + 1.0  # Oscillating scale for the beating effect
    scaled_size = size * scale

    nvg.save(vg)

    # Change coord so that we draw in coords between (-1, 1) and (-1, 1)
    nvg.translate(vg, x, y)
    nvg.scale(vg, scaled_size, -scaled_size)  # y points up

    nvg.begin_path(vg)
    nvg.move_to(vg, 0.0, 0.4)
    nvg.bezier_to(vg, 0.0, 0.5, 0.1, 1.0, 0.5, 1.0)
    nvg.bezier_to(vg, 0.9, 1.0, 1.0, 0.7, 1.0, 0.4)
    nvg.bezier_to(vg, 1.0, 0.2, 0.75, -0.2, 0.5, -0.4)
    nvg.bezier_to(vg, 0.2, -0.65, 0.0, -0.8, 0.0, -1.0)

    nvg.bezier_to(vg, 0.0, -0.8, -0.2, -0.65, -0.5, -0.4)
    nvg.bezier_to(vg, -0.75, -0.2, -1.0, 0.2, -1.0, 0.4)
    nvg.bezier_to(vg, -1.0, 0.7, -0.9, 1.0, -0.5, 1.0)
    nvg.bezier_to(vg, -0.1, 1.0, 0.0, 0.5, 0.0, 0.4)

    # Create gradient from top to bottom
    paint = nvg.linear_gradient(vg, 0.0, 1.0, 0.0, -1.0, nvg.rgba_f(1, 0, 0, 1), nvg.rgba_f(0.2, 0, 0, 1))
    nvg.fill_paint(vg, paint)
    nvg.fill(vg)

    nvg.stroke_color(vg, nvg.rgba(0, 0, 255, 255))
    nvg.stroke_width(vg, 0.05)
    nvg.stroke(vg)

    nvg.restore(vg)


def draw_nano_vg_label(vg: nvg.Context, width: float, height: float):
    # The font used to write "NanoVG": it should be loaded only once
    static = draw_nano_vg_label
    if not hasattr(static, "static_font_id"):
        # Load the font
        font_path = hello_imgui.asset_file_full_path("fonts/Roboto/Roboto-Bold.ttf")
        static.font_id = nvg.create_font(vg, "roboto", font_path)
        if static.font_id == -1:
            print("Could not add font.")
            return  # Exit if the font cannot be added.

    nvg.begin_path(vg)
    nvg.font_size(vg, 128.0)
    nvg.font_face_id(vg, static.font_id)
    nvg.text_align(vg, nvg.Align.align_center.value | nvg.Align.align_middle.value)
    nvg.save(vg)
    nvg.rotate(vg, -0.1)
    nvg.fill_color(vg, nvg.rgba(255, 100, 100, 255))
    nvg.text(vg, 0.5 * width, 0.9 * height, "NanoVG")
    nvg.restore(vg)


def draw_scene(vg: nvg.Context, width: float, height: float):
    nvg.save(vg)

    # Draw a white background
    nvg.begin_path(vg)
    nvg.rect(vg, 0, 0, width, height)
    nvg.fill_color(vg, nvg.rgba(255, 255, 255, 255))
    nvg.fill(vg)

    # Draw NanoVG
    draw_nano_vg_label(vg, width, height)

    # Draw a heart
    draw_heart(vg, ImVec2(width / 2.0, height / 2.0), width * 0.2, imgui.get_time())

    nvg.restore(vg)



class AppStateNvgHeart:
    vg: nvg.Context = None
    nvg_framebuffer: nvg_imgui.NvgFramebuffer = None

    def __init__(self):
        # Our NanoVG context
        self.vg = None

        # A framebuffer, which will be used as a texture for our button
        self.nvg_framebuffer = None

    def init(self):
        # Instantiate the NanoVG context
        self.vg = nvg_imgui.create_nvg_context_gl(nvg_imgui.NvgCreateFlags.antialias | nvg_imgui.NvgCreateFlags.stencil_strokes)

        # Create a framebuffer
        nvg_image_flags = 0  # NVG_IMAGE_FLIPY | NVG_IMAGE_PREMULTIPLIED;
        self.nvg_framebuffer = nvg_imgui.NvgFramebuffer(self.vg, 1000, 600, nvg_image_flags)

    def release(self):
        self.nvg_framebuffer = None
        nvg_imgui.delete_nvg_context_gl(self.vg)


def main():
    app_state = AppStateNvgHeart()

    runner_params = hello_imgui.RunnerParams()

    runner_params.callbacks.enqueue_post_init(lambda: app_state.init())
    runner_params.callbacks.enqueue_before_exit(lambda: app_state.release())

    # Render our drawing to a custom background:
    #   (we need to disable the default ImGui window, so that the background is visible)
    runner_params.imgui_window_params.default_imgui_window_type = hello_imgui.DefaultImGuiWindowType.no_default_window

    # CustomBackground is where we can draw our custom background
    def custom_background():
        nvg_imgui.render_nvg_to_background(app_state.vg, draw_scene)

    runner_params.callbacks.custom_background = custom_background

    def gui():
        imgui.begin("Hello, NanoVG!")

        imgui.text("Click on the image button below to exit")

        # Also, render our drawing to a framebuffer, and use it as a texture for an ImGui button
        # Render to our framebuffer
        nvg_imgui.render_nvg_to_frame_buffer(app_state.vg, app_state.nvg_framebuffer, draw_scene)
        # Use it as a texture for an ImGui button
        if imgui.image_button("ImgButton", app_state.nvg_framebuffer.texture_id, hello_imgui.em_to_vec2(5.0, 3.0)):
            hello_imgui.get_runner_params().app_shall_exit = True

        imgui.end()

    runner_params.callbacks.show_gui = gui
    runner_params.fps_idling.enable_idling = False

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()

