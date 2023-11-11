import webbrowser
from imgui_bundle import imgui, hello_imgui, immapp, ImVec4, ImVec2

ImTextureID = int


def draw_transparent_image(
    texture: ImTextureID, rect: imgui.internal.ImRect, alpha: float
):
    alpha_color = imgui.get_color_u32(ImVec4(1.0, 1.0, 1.0, alpha))
    imgui.get_foreground_draw_list().add_image_quad(
        texture,
        ImVec2(rect.min.x, rect.min.y),
        ImVec2(rect.max.x, rect.min.y),
        ImVec2(rect.max.x, rect.max.y),
        ImVec2(rect.min.x, rect.max.y),
        ImVec2(0, 0),
        ImVec2(1, 0),
        ImVec2(1, 1),
        ImVec2(0, 1),
        alpha_color,
    )


@immapp.static(start_time=-1.0, was_idling_restored=False)  # type: ignore
def animate_logo(
    logo_file: str,
    ratio_width_height: float,
    em_top_right_margin: ImVec2,
    final_alpha: float,
    url: str,
):
    static = animate_logo
    if static.start_time < 0:
        static.start_time = immapp.clock_seconds()

    logo_texture = hello_imgui.im_texture_id_from_asset(logo_file)

    def unlerp(a, b, x):
        return (x - a) / (b - a)

    def lerp(a, b, x):
        return a + (b - a) * x

    rect0: imgui.internal.ImRect = imgui.internal.ImRect()
    rect1: imgui.internal.ImRect = imgui.internal.ImRect()
    alpha0: float = 1
    alpha1: float = 1

    @immapp.run_anon_block
    def fill_positions():
        nonlocal rect0, rect1, alpha0, alpha1
        ImVec2(1.0, 1.0)
        viewport_size = imgui.get_main_viewport().size
        viewport_position = imgui.get_main_viewport().pos
        viewport_min_size = min(viewport_size.x, viewport_size.y)
        vp_center = imgui.get_main_viewport().get_center()

        size0 = ImVec2(
            viewport_min_size * 0.8, viewport_min_size * 0.8 / ratio_width_height
        )
        position0 = ImVec2(vp_center.x - size0.x / 2, vp_center.y - size0.y / 2)
        rect0 = imgui.internal.ImRect(
            position0, ImVec2(position0.x + size0.x, position0.y + size0.y)
        )
        alpha0 = 1.0

        em = imgui.get_font_size()
        size1 = ImVec2(
            viewport_min_size * 0.12 * ratio_width_height, viewport_min_size * 0.12
        )
        position1 = ImVec2(
            viewport_position.x + viewport_size.x - size1.x, viewport_position.y
        )
        position1 = ImVec2(
            position1.x - em_top_right_margin.x * em,
            position1.y + em_top_right_margin.y * em,
        )
        rect1 = imgui.internal.ImRect(
            position1, ImVec2(position1.x + size1.x, position1.y + size1.y)
        )
        alpha1 = final_alpha

    k_animation: float = 0  # between 0 and 1

    @immapp.run_anon_block
    def fill_k():
        nonlocal k_animation
        dt = immapp.clock_seconds() - static.start_time

        t_pause = 0.4
        t_animation = 0.8

        if dt < t_pause:
            k_animation = 0
        elif dt < t_animation:
            k_animation = unlerp(t_pause, t_animation, dt)
        else:
            k_animation = 1.0

    rect = imgui.internal.ImRect(
        imgui.internal.im_lerp(rect0.min, rect1.min, k_animation),
        imgui.internal.im_lerp(rect0.max, rect1.max, k_animation),
    )
    alpha = lerp(alpha0, alpha1, k_animation)

    if k_animation < 1:
        hello_imgui.get_runner_params().fps_idling.enable_idling = False
    if k_animation >= 1.0 and not static.was_idling_restored:
        hello_imgui.get_runner_params().fps_idling.enable_idling = True
        static.was_idling_restored = True

    mouse_position = imgui.get_mouse_pos()
    if rect.contains(mouse_position):
        alpha = 1
        if imgui.is_mouse_clicked(0):
            webbrowser.open(url)

    draw_transparent_image(logo_texture, rect, alpha)
