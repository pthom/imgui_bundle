
import importlib.util
_has_opencv = importlib.util.find_spec("cv2") is not None

from imgui_bundle.demos_python.demos_immvision import (  # noqa: E402
    demo_immvision_display,
    demo_immvision_inspector,
    demo_immvision_inspector_mandelbrot,
    demo_immvision_link,
    demo_immvision_no_opencv,
)
if _has_opencv:
    from imgui_bundle.demos_python.demos_immvision import demo_immvision_process  # noqa: F401

__all__ = [
    "demo_immvision_display",
    "demo_immvision_inspector",
    "demo_immvision_inspector_mandelbrot",
    "demo_immvision_link",
    "demo_immvision_no_opencv",
]
if _has_opencv:
    __all__.append("demo_immvision_process")
