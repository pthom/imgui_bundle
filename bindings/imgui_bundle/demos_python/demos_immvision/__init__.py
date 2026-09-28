
import importlib.util
_has_opencv = importlib.util.find_spec("cv2") is not None

# The demos read their images with OpenCV
if _has_opencv:
    from imgui_bundle.demos_python.demos_immvision import (  # noqa: E402, F401
        demo_immvision_display,
        demo_immvision_inspector,
        demo_immvision_link,
        demo_immvision_process,
    )

__all__ = []
if _has_opencv:
    __all__ += ["demo_immvision_display", "demo_immvision_inspector", "demo_immvision_link", "demo_immvision_process"]
