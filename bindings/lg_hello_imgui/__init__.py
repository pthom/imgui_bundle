from lg_hello_imgui._lg_hello_imgui import imgui
from lg_hello_imgui._lg_hello_imgui import hello_imgui
from lg_hello_imgui._lg_hello_imgui import implot

import os
THIS_DIR = os.path.dirname(__file__)
hello_imgui.override_assets_folder(THIS_DIR + "/assets")
