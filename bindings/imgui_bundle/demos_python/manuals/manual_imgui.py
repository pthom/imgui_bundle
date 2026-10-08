"""Dear ImGui: the interactive manual

Every widget and feature of [Dear ImGui](https://github.com/ocornut/imgui), section by section, with the Python and
C++ code of each beside it. From [Dear ImGui Explorer](https://pthom.github.io/imgui_explorer/), the interactive
manual for Dear ImGui and its libraries.
"""
from imgui_bundle import imgui, immapp, rich_md, register_demos_assets_folder

try:
    from imgui_bundle.demos_python.manuals.manual_common import show_manual
except ImportError:  # a script: the module is beside this file
    from manual_common import show_manual  # type: ignore[import-not-found, no-redef]

try:  # the logo needs the demos' utilities and assets
    from imgui_bundle.demos_python.demo_utils.animate_logo import animate_logo
    register_demos_assets_folder()
    HAS_LOGO = True
except ImportError:  # the playground ships neither: no logo there
    HAS_LOGO = False

FPS_IDLE = 30.0  # when idle: its demos animate, and they are not ours to mark as live (set_item_is_live)


def gui() -> None:
    if HAS_LOGO:  # it lands at the top right of the page, beside the title
        animate_logo("images/logo_imgui_600.jpg", 2.0, 0.45, "https://github.com/ocornut/imgui")
    rich_md.render("""
        # Dear ImGui
        Browse the demos below, and look at their code in the right panel! You may switch between C++ and Python code
        with the toggle at the top right.
    """)
    imgui.separator()
    show_manual("imgui", fallback=lambda: imgui.show_demo_window())


if __name__ == "__main__":
    immapp.run(gui, window_size=(1100, 800), with_markdown=True, fps_idle=FPS_IDLE)
