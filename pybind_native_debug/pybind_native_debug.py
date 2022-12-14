#!/usr/bin/env python3
import os
import sys

THIS_DIR = os.path.dirname(__file__)


def main() -> None:
    path_demos = os.path.realpath(f"{THIS_DIR}/../bindings/imgui_bundle/demos")
    print(path_demos)
    sys.path.append(path_demos)

    path_demos_immvision = path_demos + "/demos_immvision"
    sys.path.append(path_demos_immvision)

    import demo_inspector  # type: ignore

    demo_inspector.main()


main()
