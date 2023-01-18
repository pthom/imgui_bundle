# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
def test_version():
    import imgui_bundle

    assert imgui_bundle.__version__ >= "0.6.0"
