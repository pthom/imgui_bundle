# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""The final screenshot keeps the rows of the framebuffer in order (the middle rows too, for an even height)."""
import numpy as np
from PIL import Image
from imgui_bundle import imgui
from imgui_bundle.immapp import testing


def test_final_app_window_screenshot_rows_in_order(tmp_path) -> None:  # type: ignore[no-untyped-def]
    def gui() -> None:
        # A vertical gradient over the whole window: black at the top, white at the bottom
        black, white = imgui.IM_COL32(0, 0, 0, 255), imgui.IM_COL32(255, 255, 255, 255)
        imgui.get_foreground_draw_list().add_rect_filled_multi_color(
            (0, 0), imgui.get_io().display_size, black, black, white, white)

    path = testing.capture_final_frame(gui, tmp_path / "gradient.png", window_size=(64, 100))
    rows = np.asarray(Image.open(path).convert("L"), dtype=np.int32).mean(axis=1)
    assert len(rows) % 2 == 0, "the bug needs an even height"
    assert (np.diff(rows) >= 0).all(), f"rows out of order around row {int(np.argmin(np.diff(rows)))} of {len(rows)}"
