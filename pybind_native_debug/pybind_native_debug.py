# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import imgui, hello_imgui


# "Call any function from the library which you want to debug
hello_imgui.run(lambda: imgui.text("hello"))
