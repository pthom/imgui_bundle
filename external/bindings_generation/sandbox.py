# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os
from bindings_generation.all_external_libraries import *
from bindings_generation.paths import repo_dir


def sandbox():
    os.chdir(repo_dir())
    for lib in ALL_LIBS:
        if lib.fork_git_url is None:
            print(lib.name)


if __name__ == "__main__":
    sandbox()
