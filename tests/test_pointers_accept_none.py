# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""The current contexts may be None: their setters take None, their getters return it (issue #512). No GUI needed."""
import sys


def test_current_contexts_accept_none() -> None:
    # We skip windows, see note at the top of lg_imgui_bundle_test.py
    if sys.platform == "win32":
        return

    import imgui_bundle
    from imgui_bundle import imgui

    imgui_context = imgui.create_context()

    # The other libraries are tested when the build has them (the minimal wheels lack some of them)
    if imgui_bundle.has_submodule("implot"):
        from imgui_bundle import implot

        implot_context = implot.create_context()
        implot.set_current_context(None)
        assert implot.get_current_context() is None
        implot.set_current_context(implot_context)
        implot.destroy_context(implot_context)

    if imgui_bundle.has_submodule("implot3d"):
        from imgui_bundle import implot3d

        implot3d_context = implot3d.create_context()
        implot3d.set_current_context(None)
        assert implot3d.get_current_context() is None
        implot3d.set_current_context(implot3d_context)
        implot3d.destroy_context(implot3d_context)

    if imgui_bundle.has_submodule("imgui_node_editor"):
        from imgui_bundle import imgui_node_editor

        imgui_node_editor.set_current_editor(None)
        assert imgui_node_editor.get_current_editor() is None

    if imgui_bundle.has_submodule("rich_md"):
        from imgui_bundle import rich_md

        rich_md.set_current_context(None)
        assert rich_md.get_current_context() is None

    imgui.set_current_context(None)
    assert imgui.get_current_context() is None
    imgui.set_current_context(imgui_context)
    imgui.destroy_context(imgui_context)
