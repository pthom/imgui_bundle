# Demo gradient with ImGuizmo
# See equivalent C++ program: demos_cpp/demos_imguizmo/demo_guizmo_zoom_slider.main.cpp

from imgui_bundle import imgui, ImVec4, ImVec2, imguizmo, run_anon_block
from imgui_bundle.demos.demos_imguizmo.demos_interface import GuiFunction
import imgui_bundle


ImZoomSlider = imguizmo.ImZoomSlider

import numpy as np


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
            imgui.get_foreground_draw_list().add_line(ImVec2(x_win, rect_min.y), ImVec2(x_win, rect_max.y), color)
    for y in np.arange(0, 1, 0.05):
        y_win = to_y_window_coord(y)
        if rect_min.y <= y_win < rect_max.y:
            imgui.get_foreground_draw_list().add_line(ImVec2(rect_min.x, y_win), ImVec2(rect_max.x, y_win), color)


# This returns a closure function that will later be invoked to run the app
def make_closure_demo_guizmo_zoom_slider() -> GuiFunction:
    # Values between 0. and 1. that represent the current viewed portion
    view_min = ImVec2(0.1, 0.3)
    view_max = ImVec2(0.6, 0.8)
    link_zooms = True

    def gui():
        nonlocal link_zooms, view_min, view_max
        _, link_zooms = imgui.checkbox("Link zooms", link_zooms)

        # Draw anything in the zoomable part,
        # or reserve some space (for example with imgui.Dummy)
        @run_anon_block
        def _():
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
            {view_min.x=:.2f} {view_max.x=:.2f}
            {view_min.y=:.2f} {view_max.y=:.2f} 
    
            ...now do whatever you want with those values!"""
            )

            imgui.dummy(ImVec2(zone_width, 80))
            imgui.end_group()

        # Get the zoomable part size (which may have been reserved by ImGui:Dummy)
        zoomZoneMin = imgui.get_item_rect_min()
        zoomZoneMax = imgui.get_item_rect_max()

        # And do some drawing depending on the zoom
        draw_zoomable_grid(zoomZoneMin, zoomZoneMax, view_min, view_max)

        # Draw the vertical slider
        imgui.same_line()
        imgui.push_id(18)
        changed, view_min.y, view_max.y = imguizmo.ImZoomSlider.im_zoom_slider_stl(
            0.0, 1.0, view_min.y, view_max.y, 0.1, ImZoomSlider.ImGuiZoomSliderFlags_.vertical
        )
        # Handle link zoom
        if changed and link_zooms:
            avg = (view_min.x + view_max.x) / 2.0
            length = view_max.y - view_min.y
            view_min.x = avg - length / 2.0
            view_max.x = avg + length / 2.0
        imgui.pop_id()

        # Draw the horizontal slider
        imgui.push_id(19)
        changed, view_min.x, view_max.x = ImZoomSlider.im_zoom_slider_stl(0.0, 1.0, view_min.x, view_max.x, 0.1)
        # Handle link zoom
        if changed and link_zooms:
            avg = (view_min.y + view_max.y) / 2.0
            length = view_max.x - view_min.x
            view_min.y = avg - length / 2.0
            view_max.y = avg + length / 2.0
        imgui.pop_id()

    return gui


def main():
    gui = make_closure_demo_guizmo_zoom_slider()
    imgui_bundle.run(gui, window_size=(400, 400))


if __name__ == "__main__":
    main()
