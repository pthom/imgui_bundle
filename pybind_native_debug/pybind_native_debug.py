#!/usr/bin/env python3
# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os
import sys

THIS_DIR = os.path.dirname(__file__)


def main() -> None:
    path_bindings = os.path.realpath(f"{THIS_DIR}/../bindings/")
    sys.path = [path_bindings] + sys.path

    from imgui_bundle.demos_python import demo_node_editor_launcher

    demo_node_editor_launcher.main()


main()
