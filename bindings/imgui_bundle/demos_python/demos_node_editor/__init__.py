import importlib.util

from imgui_bundle.demos_python.demos_node_editor import demo_node_editor_color_mixer  # noqa: F401

# The image pipeline filters its images with OpenCV
if importlib.util.find_spec("cv2") is not None:
    from imgui_bundle.demos_python.demos_node_editor import demo_node_editor_image_pipeline  # noqa: E402, F401
