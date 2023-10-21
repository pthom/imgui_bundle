# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os
from bindings_generation import all_external_libraries


def sandbox():
    pass


if __name__ == "__main__":
    all_external_libraries.reattach_all_submodules()
    # all_external_libraries.pull_all_submodules()
