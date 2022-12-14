from typing import Callable


GuiFunction = Callable[[], None]


def demos_assets_folder() -> str:
    import os

    this_dir = os.path.dirname(__file__)
    r = os.path.abspath(f"{this_dir}/../assets")
    return r
