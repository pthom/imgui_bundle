# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os


def external_libraries_dir():
    this_dir = os.path.abspath(os.path.dirname(__file__) + "/..")
    return this_dir


def repo_dir():
    r = os.path.abspath(external_libraries_dir() + "/..")
    return r
