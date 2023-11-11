# Demo gradient with ImGuizmo
# See equivalent C++ program: demos_cpp/demos_imguizmo/demo_guizmo_zoom_slider.main.cpp

###############################################################################
# Warning! This component does not render well on high DPI
# (especially under windows) => this demo is hidden by default
###############################################################################


from imgui_bundle import imgui, ImVec4, ImVec2, imguizmo, immapp
from imgui_bundle.demos_python.demo_utils.api_demos import GuiFunction
import numpy as np

im_zoom_slider = imguizmo.im_zoom_slider


def lerp(a: float, b: float, x: float):
    """linear interpolation"""
    return a + (b - a) * x


# The zoomable grid on the background
def draw_zoomable_grid(
    rect_min: ImVec2,
    rect_max: ImVec2,  # Those are pixels
    view_min: ImVec2,
    view_max: ImVec2,  # Those are values between 0 and 1
):
    def to_x_window_coord(x: float):
        kx = (x - view_min.x) / (view_max.x - view_min.x)
        return lerp(rect_min.x, rect_max.x, kx)

    def to_y_window_coord(y: float):
        ky = (y - view_min.y) / (view_max.y - view_min.y)
        return lerp(rect_min.y, rect_max.y, ky)

    color = imgui.get_color_u32(ImVec4(1, 1, 1, 0.2))
    for x in np.arange(0, 1, 0.05):
        x_win = to_x_window_coord(x)
        if rect_min.x <= x_win < rect_max.x:
            imgui.get_foreground_draw_list().add_line(
                ImVec2(x_win, rect_min.y), ImVec2(x_win, rect_max.y), color
            )
    for y in np.arange(0, 1, 0.05):
        y_win = to_y_window_coord(y)
        if rect_min.y <= y_win < rect_max.y:
            imgui.get_foreground_draw_list().add_line(
                ImVec2(rect_min.x, y_win), ImVec2(rect_max.x, y_win), color
            )


# This returns a closure function that will later be invoked to run the app
def make_closure_demo_guizmo_zoom_slider() -> GuiFunction:
    # Values between 0. and 1. that represent the current viewed portion
    view_horizontal = im_zoom_slider.Range(0.1, 0.6)
    view_vertical = im_zoom_slider.Range(0.3, 0.8)

    link_zooms = True

    def gui():
        nonlocal link_zooms, view_horizontal, view_vertical
        _, link_zooms = imgui.checkbox("Link zooms", link_zooms)

        # Draw anything in the zoomable part,
        # or reserve some space (for example with imgui.Dummy)
        @immapp.run_anon_block
        def _block():
            zone_width = 380.0
            imgui.begin_group()
            # If needed, just use imgui.Dummy to reserve some space
            imgui.dummy(ImVec2(zone_width, 80))
            imgui.text(
                f"""
            You are looking at a zoomable part:
            use the mouse wheel on the sliders,
            or drag their extremities.

            Current zoom values:
            {view_horizontal.min=:.2f} {view_horizontal.max=:.2f}
            {view_vertical.min=:.2f} {view_vertical.max=:.2f}

            ...now do whatever you want with those values!"""
            )

            imgui.dummy(ImVec2(zone_width, 80))
            imgui.end_group()

        # Get the zoomable part size (which may have been reserved by ImGui:Dummy)
        zoomZoneMin = imgui.get_item_rect_min()
        zoomZoneMax = imgui.get_item_rect_max()

        # And do some drawing depending on the zoom
        draw_zoomable_grid(
            zoomZoneMin,
            zoomZoneMax,
            ImVec2(view_horizontal.min, view_vertical.min),
            ImVec2(view_horizontal.max, view_vertical.max),
        )

        # Draw the vertical slider
        imgui.same_line()
        imgui.push_id(18)
        sliderResult = im_zoom_slider.im_zoom_slider_pure(
            im_zoom_slider.Range(0.0, 1.0),
            view_vertical,
            0.1,
            im_zoom_slider.ImGuiZoomSliderFlags_.vertical,
        )
        if sliderResult:
            view_vertical = sliderResult.value
        # Handle link zoom
        if sliderResult and link_zooms:
            avgH = view_horizontal.center()
            lengthV = view_vertical.length()
            view_horizontal = im_zoom_slider.Range(
                avgH - lengthV / 2.0, avgH + lengthV / 2.0
            )
        imgui.pop_id()

        # Draw the horizontal slider
        imgui.push_id(19)
        sliderResult = im_zoom_slider.im_zoom_slider_pure(
            im_zoom_slider.Range(0.0, 1.0), view_horizontal, 0.1
        )
        if sliderResult:
            view_horizontal = sliderResult.value

        # Handle link zoom
        if sliderResult and link_zooms:
            avgV = view_vertical.center()
            lengthH = view_horizontal.length()
            view_horizontal = im_zoom_slider.Range(
                avgV - lengthH / 2.0, avgV + lengthH / 2.0
            )
        imgui.pop_id()

    return gui


@immapp.static(gui=None)
def demo_launch():
    statics = demo_launch
    if statics.gui is None:
        statics.gui = make_closure_demo_guizmo_zoom_slider()
    statics.gui()


def main():
    gui = make_closure_demo_guizmo_zoom_slider()
    immapp.run(gui, window_size=(400, 400))


if __name__ == "__main__":
    main()
