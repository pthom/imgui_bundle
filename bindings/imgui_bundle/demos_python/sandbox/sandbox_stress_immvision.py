"""Stress test for ImmVision: live camera feed with shared zoom.

Displays the camera image.
The image is updated every frame (RefreshImage=True).

Usage: python sandbox_stress_immvision.py
Requires: opencv-python (for camera capture)
"""

import numpy as np
from imgui_bundle import immvision, immapp, imgui

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


class AppState:
    def __init__(self):
        self.camera: "cv2.VideoCapture | None" = None
        self.frame: np.ndarray = np.zeros((480, 640, 3), dtype=np.uint8)

        self.params_full = immvision.ImageParams()
        self.params_full.image_display_size = (400, 0)
        self.params_full.zoom_key = "shared"
        self.params_full.refresh_image = True

    def init_camera(self):
        if HAS_CV2:
            self.camera = cv2.VideoCapture(1)

    def grab_frame(self):
        if self.camera is not None and self.camera.isOpened():
            ret, self.frame = self.camera.read()


state = AppState()


def gui():
    state.grab_frame()

    imgui.text(f"FPS: {imgui.get_io().framerate:.1f}")
    if state.camera is None or not state.camera.isOpened():
        imgui.text("(No camera — showing synthetic animation)")
    immvision.image("Full##stress", state.frame, state.params_full)


def main():
    immvision.use_bgr_color_order()
    state.init_camera()
    immapp.run(gui, window_title="ImmVision Stress Test", window_size=(900, 600), fps_idle=0.0)


if __name__ == "__main__":
    main()
