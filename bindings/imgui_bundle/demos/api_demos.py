from typing import Callable


GuiFunction = Callable[[], None]


def demos_assets_folder():
    import os
    this_dir = os.path.dirname(__file__)
    r = f"{this_dir}/assets"
    return r
