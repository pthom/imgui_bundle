#!/usr/bin/env python3
import os
import sys

THIS_DIR = os.path.dirname(__file__)


def main() -> None:
    path_lg_imgui_bundle = os.path.realpath(f"{THIS_DIR}/../demos_python")
    print(path_lg_imgui_bundle)
    sys.path.append(path_lg_imgui_bundle)

    import demo_node_editor  # type: ignore

    demo_node_editor.main()


main()
