# demo_tex_inspect_demo_window
# See equivalent C++ program: demos_cpp/demos_tex_inspect/demo_tex_inspect_demo_window.cpp
#
# This app launches an internal demo from imgui_tex_inspect, thus its code does not appear here.
#
from imgui_bundle import imgui_tex_inspect, hello_imgui, immapp
from imgui_bundle.demos_python.demo_utils.api_demos import demos_assets_folder


def main():
    hello_imgui.set_assets_folder(demos_assets_folder())
    immapp.run(
        imgui_tex_inspect.show_demo_window,
        with_tex_inspect=True,
        with_markdown=True,
        window_size=(1200, 1000),
    )


if __name__ == "__main__":
    main()
