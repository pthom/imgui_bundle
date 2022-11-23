#!/usr/bin/env python3
import os
import sys

THIS_DIR = os.path.dirname(__file__)


def main() -> None:
    path_demos = os.path.realpath(f"{THIS_DIR}/../demos_python")
    print(path_demos)
    sys.path.append(path_demos)

    path_demos = os.path.realpath(f"{THIS_DIR}/../demos_python/node_fn_compose/")
    sys.path.append(path_demos)

    import demo_compose_image_debug  # type: ignore

    demo_compose_image_debug.main()


main()
