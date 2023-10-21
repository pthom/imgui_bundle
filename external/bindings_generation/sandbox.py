# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os
from bindings_generation.all_external_libraries import *
from bindings_generation.paths import repo_dir


def reattach_all_submodule():
    os.chdir(repo_dir())
    for lib in ALL_LIBS:
        print(lib.name)
        lib.run_reattach_submodule()


def sandbox():
    pass


if __name__ == "__main__":
    reattach_all_submodule()
