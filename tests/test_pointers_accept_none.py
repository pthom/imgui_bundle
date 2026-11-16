# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""The current contexts may be None: their setters take None, their getters return it (issue #512). No GUI needed."""
import sys


def test_current_contexts_accept_none() -> None:
    # We skip windows, see note at the top of lg_imgui_bundle_test.py
    if sys.platform == "win32":
        return

    from imgui_bundle import imgui, implot, implot3d, imgui_node_editor, rich_md

    imgui_context = imgui.create_context()

    implot_context = implot.create_context()
    implot.set_current_context(None)
    assert implot.get_current_context() is None
    implot.set_current_context(implot_context)
    implot.destroy_context(implot_context)

    implot3d_context = implot3d.create_context()
    implot3d.set_current_context(None)
    assert implot3d.get_current_context() is None
    implot3d.set_current_context(implot3d_context)
    implot3d.destroy_context(implot3d_context)

    imgui_node_editor.set_current_editor(None)
    assert imgui_node_editor.get_current_editor() is None
    rich_md.set_current_context(None)
    assert rich_md.get_current_context() is None

    imgui.set_current_context(None)
    assert imgui.get_current_context() is None
    imgui.set_current_context(imgui_context)
    imgui.destroy_context(imgui_context)
