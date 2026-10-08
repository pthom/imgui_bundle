"""What the four manual cards share: the imgui_explorer tooling opened on one library"""
import os
from typing import Callable

from imgui_bundle import imgui, rich_md, hello_imgui

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


NARROW_WIDTH_EM = 50.0  # under this width, the explorer shows one pane at a time (kNarrowWidthEm, imgui_explorer.cpp)


def show_intro(title: str, line: str = "") -> None:
    """The manual's title, a line about the library, and how to read the manual: the code beside the demos, or, one
    pane at a time on a narrow screen, behind the switch to the code view"""
    if imgui.get_content_region_avail().x < hello_imgui.em_size(NARROW_WIDTH_EM):
        hint = "Browse the demos below, and when you want to see the code for one of them, switch to the code view."
    else:
        hint = "Browse the demos below, and read their code beside them."
    rich_md.render(f"# {title}\n" + (f"{line} {hint}" if line else hint))
    imgui.separator()


def show_manual(library: str, fallback: Callable[[], object]) -> None:
    """The interactive manual of a library ("imgui", "implot", "implot3_d", "im_anim"): its demo, section by
    section, with the code of each beside it. Without the tooling, the plain demo"""
    if HAS_EXPLORER:
        imgui_explorer.show_imgui_explorer_gui_python(getattr(imgui_explorer.ImGuiExplorerLibrary, library),
                                                      package_path())
    else:
        fallback()

