"""Tex Inspect: the full demo

The demo window of [imgui_tex_inspect](https://github.com/andyborrell/imgui_tex_inspect): every way to inspect a
texture, with its options (grid, alpha, channels, zoom). The demo lives in the library: this file only opens it.
"""
# See equivalent C++ program: demos_cpp/demos_tex_inspect/demo_tex_inspect_demo_window.cpp
from imgui_bundle import imgui_tex_inspect, immapp, register_demos_assets_folder

register_demos_assets_folder()

def main():
    immapp.run(
        imgui_tex_inspect.show_demo_window,
        with_tex_inspect=True,
        with_markdown=True,
        window_size=(1200, 1000),
    )


if __name__ == "__main__":
    main()
