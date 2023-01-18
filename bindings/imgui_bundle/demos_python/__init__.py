# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os
from imgui_bundle import hello_imgui

this_dir = os.path.dirname(__file__)
assets_folder = this_dir + "/assets"
hello_imgui.set_assets_folder(assets_folder)
