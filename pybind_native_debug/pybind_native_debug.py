#!/usr/bin/env python3
import os
import sys

THIS_DIR = os.path.dirname(__file__)


def main() -> None:
    path_demos = os.path.realpath(f"{THIS_DIR}/../demos_python")
    print(path_demos)
    sys.path.append(path_demos)

    path_demos = os.path.realpath(f"{THIS_DIR}/../demos_python/demo_composition_graph/")
    sys.path.append(path_demos)

    path_demos = os.path.realpath(f"{THIS_DIR}/../demos_python/demos_imguizmo/")
    sys.path.append(path_demos)

    import demo_guizmo_stl  # type: ignore

    demo_guizmo_stl.main()


main()
