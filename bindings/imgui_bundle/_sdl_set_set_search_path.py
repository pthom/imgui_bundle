# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle


def _sdl2_set_set_search_path() -> None:
    """Sets os.environ["PYSDL2_DLL_PATH"] so that SDL2 provided by PySDL2 uses our SDL2 library."""
    import os

    this_dir = os.path.dirname(__file__)
    os.environ["PYSDL2_DLL_PATH"] = this_dir

def _sdl3_set_set_search_path() -> None:
    """Sets os.environ["SDL_BINARY_PATH"] so that SDL3 provided by PySDL3 uses our SDL3 library."""
    import os

    this_dir = os.path.dirname(__file__)
    os.environ["SDL_BINARY_PATH"] = this_dir
