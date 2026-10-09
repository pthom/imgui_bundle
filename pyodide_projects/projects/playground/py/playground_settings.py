"""The settings of the playground's page, applied to each demo: a theme and a font scale (js/settings.js).

The page loads this module once Pyodide is ready, and calls its functions. A demo gets the settings after its setup,
before its first frame (pyodide_patch_runners.after_setup_callbacks). A demo with a theme of its own ("own_theme" in
examples.json) keeps it, until the user picks a theme while it runs.
"""
from imgui_bundle import hello_imgui, imgui, pyodide_patch_runners

_theme_name = ""  # the theme picked in the page; "" before any pick: each demo keeps its own
_font_scale = 1.0  # imgui's style.font_scale_main
_demo_has_own_theme = False  # the demo about to start sets a theme of its own
_theme_at_start = ""  # the running demo's theme after its setup: a change after it is the user's pick


def current_theme() -> str:
    """The theme of the running demo"""
    return hello_imgui.imgui_theme_name(hello_imgui.get_runner_params().imgui_window_params.tweaked_theme.theme)


def _apply_theme(theme_name: str) -> None:
    """The running demo takes this theme, with its own tweaks (rounding, colors)"""
    tweaked_theme = hello_imgui.get_runner_params().imgui_window_params.tweaked_theme
    tweaked_theme.theme = hello_imgui.imgui_theme_from_name(theme_name)
    hello_imgui.apply_tweaked_theme(tweaked_theme)


def _after_setup() -> None:
    global _theme_at_start
    if _theme_name and not _demo_has_own_theme:
        _apply_theme(_theme_name)
    imgui.get_style().font_scale_main = _font_scale
    _theme_at_start = current_theme()


pyodide_patch_runners.after_setup_callbacks.append(_after_setup)


# The functions the page calls
def configure(theme_name: str, font_scale: float) -> None:
    """The settings kept by the page (its localStorage), at its start"""
    global _theme_name, _font_scale
    _theme_name, _font_scale = theme_name, font_scale


def next_demo(own_theme: bool) -> None:
    """Before a demo runs: does it set a theme of its own?"""
    global _demo_has_own_theme
    _demo_has_own_theme = own_theme


def set_theme(theme_name: str) -> None:
    """The user picks a theme: the running demo takes it, and the next ones"""
    global _theme_name, _theme_at_start
    _theme_name = theme_name
    if pyodide_patch_runners.is_renderer_running():
        _apply_theme(theme_name)
        _theme_at_start = theme_name


def set_font_scale(font_scale: float) -> None:
    """The user changes the font size: the running demo takes it, and the next ones"""
    global _font_scale
    _font_scale = font_scale
    if pyodide_patch_runners.is_renderer_running():
        imgui.get_style().font_scale_main = font_scale


def theme_picked_in_demo() -> str:
    """The theme the user picked inside the running demo (the themes demo, a menu), or "": called before it stops"""
    if not pyodide_patch_runners.is_renderer_running():
        return ""
    theme_name = current_theme()
    return theme_name if theme_name != _theme_at_start else ""
