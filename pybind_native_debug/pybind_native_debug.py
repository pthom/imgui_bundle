#!/usr/bin/env python3
import os
import sys

THIS_DIR = os.path.dirname(__file__)


def main() -> None:
    path_lg_imgui_bundle = os.path.realpath(f"{THIS_DIR}/../demos_python")
    print(path_lg_imgui_bundle)
    sys.path.append(path_lg_imgui_bundle)

    import imgui_example_outer_glfw_opengl3  # type: ignore

    imgui_example_outer_glfw_opengl3.main()


main()
