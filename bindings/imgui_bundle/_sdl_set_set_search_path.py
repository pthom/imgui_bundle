# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle


def _sdl_set_set_search_path() -> None:
    """Sets os.environ["PYSDL2_DLL_PATH"] so that SDL2 provided by PySDL2 uses our SDL2 library."""
    import os

    this_dir = os.path.dirname(__file__)
    os.environ["PYSDL2_DLL_PATH"] = this_dir
