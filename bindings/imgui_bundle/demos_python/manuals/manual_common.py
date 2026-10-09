"""What the four manual cards share: the imgui_explorer tooling opened on one library"""
import os
from typing import Callable

try:
    from imgui_bundle import imgui_explorer
    HAS_EXPLORER = True
except ImportError:  # a build without the imgui_explorer library
    HAS_EXPLORER = False


def package_path() -> str:
    """The root of the imgui_bundle package: on the desktop, the tooling reads the demos' code and the stubs there.
    In the browser it fetches them from the page's demo_code/ folder (the web explorer's, served by the playground)"""
    import imgui_bundle
    return os.path.dirname(os.path.abspath(imgui_bundle.__file__))


def show_manual(library: str, fallback: Callable[[], object]) -> None:
    """The interactive manual of a library ("imgui", "implot", "implot3_d", "im_anim"): its demo, section by
    section, with the code of each beside it. Without the tooling, the plain demo"""
    if HAS_EXPLORER:
        imgui_explorer.show_imgui_explorer_gui_python(getattr(imgui_explorer.ImGuiExplorerLibrary, library),
                                                      package_path())
    else:
        fallback()

