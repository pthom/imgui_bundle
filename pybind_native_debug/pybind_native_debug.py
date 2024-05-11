# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import imgui, hello_imgui


# "Call any function from the library which you want to debug
hello_imgui.run(lambda: imgui.text("hello"))

# Private test for the author
# import sys
# sys.path.append("/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/fiatlight/src/python")
#
# from fiatlight.fiat_kits.experimental.fiat_audio_simple.demos import blah
# blah.main()
