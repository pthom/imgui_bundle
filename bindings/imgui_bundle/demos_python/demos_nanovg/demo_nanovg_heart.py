from imgui_bundle import hello_imgui, imgui, nanovg as nvg, ImVec2
import math
from typing import List

nvg_imgui = nvg.nvg_imgui


class DrawingState:
    heart_color: List[float]

    def __init__(self):
        self.heart_color = [1.0, 0.0, 0.0, 1.0]

gDrawingState = DrawingState()


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
    color = gDrawingState.heart_color
    color_full = nvg.rgba_f(color[0], color[1], color[2], color[3])
    color_transparent = nvg.rgba_f(color[0], color[1], color[2], 0.2)
    paint = nvg.linear_gradient(vg, 0.0, 1.0, 0.0, -1.0, color_full, color_transparent)
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

        # A framebuffer, which will be used as a texture for the ImGui rendering
        self.nvg_framebuffer = None

    def init(self):
        # Instantiate the NanoVG context
        self.vg = nvg_imgui.create_nvg_context_hello_imgui(nvg_imgui.NvgCreateFlags.antialias | nvg_imgui.NvgCreateFlags.stencil_strokes)

        # Create a framebuffer
        nvg_image_flags = 0  # NVG_IMAGE_FLIPY | NVG_IMAGE_PREMULTIPLIED;
        self.nvg_framebuffer = nvg_imgui.NvgFramebuffer(self.vg, 1000, 600, nvg_image_flags)

    def release(self):
        self.nvg_framebuffer = None
        nvg_imgui.delete_nvg_context_hello_imgui(self.vg)


def main():
    app_state = AppStateNvgHeart()

    runner_params = hello_imgui.RunnerParams()

    runner_params.callbacks.enqueue_post_init(lambda: app_state.init())
    runner_params.callbacks.enqueue_before_exit(lambda: app_state.release())

    def gui():
        imgui.text("This image below is rendered by NanoVG, via a framebuffer.")

        # Render our drawing to a framebuffer, and use it as a texture for ImGui
        nvg_imgui.render_nvg_to_frame_buffer(app_state.vg, app_state.nvg_framebuffer, draw_scene)
        imgui.image(app_state.nvg_framebuffer.texture_id, hello_imgui.em_to_vec2(50, 30))

        _, gDrawingState.heart_color = imgui.color_edit4("Heart color", gDrawingState.heart_color)

    runner_params.callbacks.show_gui = gui
    runner_params.fps_idling.enable_idling = False

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()

