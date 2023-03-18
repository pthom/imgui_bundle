# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from typing import cast

try:
    import sdl2  # type: ignore

    # Fixme: the value returned below seem to not work correctly:
    #  SDL accepts them, but wont' do anything when we use them.  Probably some tricky cast required
    #  ==> they are disabled

    # def sdl2_window_hello_imgui() -> sdl2.SDL_Window:
    #     "Returns the main SDL window used by HelloImGui (when the backend is SDL2)"
    #     import ctypes
    #     from imgui_bundle import hello_imgui
    #
    #     window_address: int = hello_imgui.get_sdl_window_address()  # type: ignore
    #     # window_pointer = ctypes.cast(window_address, ctypes.POINTER(sdl2.SDL_Window))
    #     # return cast(sdl2.SDL_Window, window_pointer)
    #
    #     window_casted = sdl2.SDL_Window(window_address)
    #     return window_casted
    #
    #
    # def sdl2_gl_context_hello_imgui() -> sdl2.SDL_GLContext:
    #     "Returns the OpenGl Context used by HelloImGui (when the backend is SDL2)"
    #     import ctypes
    #     from imgui_bundle import hello_imgui
    #
    #     gl_context_address = hello_imgui.get_sdl_gl_context()  # type: ignore
    #     gl_context_pointer = ctypes.cast(gl_context_address, ctypes.POINTER(sdl2.SDL_GLContext))
    #     return cast(sdl2.SDL_GLContext, gl_context_pointer)

except ImportError:
    pass
