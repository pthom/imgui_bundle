# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle

# Notes:
# - lots of automated tests are performed in the CI pipeline, see .github/workflows/ci_automation_test.yml
#   They are performed on Windows and Linux after a pip install
# - this file is used to test binary wheels produced by cibuildwheel, and especially if imgui.create_context() works

def test_version():
    import imgui_bundle
    assert imgui_bundle.__version__ >= "0.6.0"


def test_imgui_context_creation():
    # Check that this complex issue is fixed:
    #     https://github.com/pthom/imgui_bundle/issues/170#issuecomment-1900100904
    from imgui_bundle import imgui

    ctx = imgui.create_context()
    assert ctx is not None
    imgui.destroy_context(ctx)
