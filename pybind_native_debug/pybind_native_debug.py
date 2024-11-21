# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import imgui, hello_imgui, immapp, implot

# Set the assets folder path
from imgui_bundle.demos_python import demo_utils
from imgui_bundle import hello_imgui
hello_imgui.set_assets_folder(demo_utils.demos_assets_folder())

from imgui_bundle.demos_python.demos_immapp import demo_testengine
demo_testengine.main()

# # "Call any function from the library which you want to debug
# hello_imgui.run(lambda: imgui.text("hello"))

# Private test for the author
# import sys
# sys.path.append("/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/fiatlight/src/python")
#
# from fiatlight.fiat_kits.experimental.fiat_audio_simple.demos import blah
# blah.main()
