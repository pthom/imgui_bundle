from lg_imgui_bundle._lg_imgui_bundle import imgui as imgui
from lg_imgui_bundle._lg_imgui_bundle import hello_imgui as hello_imgui
from lg_imgui_bundle._lg_imgui_bundle import implot as implot
from lg_imgui_bundle import icons_fontawesome
from lg_imgui_bundle._lg_imgui_bundle import __version__

import os
THIS_DIR = os.path.dirname(__file__)
hello_imgui.override_assets_folder(THIS_DIR + "/assets")
