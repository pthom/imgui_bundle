from lg_imgui_bundle._lg_imgui_bundle import imgui
from lg_imgui_bundle._lg_imgui_bundle import hello_imgui
from lg_imgui_bundle._lg_imgui_bundle import implot

import os
THIS_DIR = os.path.dirname(__file__)
hello_imgui.override_assets_folder(THIS_DIR + "/assets")
