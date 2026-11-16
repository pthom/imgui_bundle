# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""The text editor's language may be None: no language, the default (issue #512). No GUI needed."""
import sys


def test_set_language_none() -> None:
    # We skip windows, see note at the top of lg_imgui_bundle_test.py
    if sys.platform == "win32":
        return

    from imgui_bundle.imgui_color_text_edit import TextEditor, TextDiff

    editor = TextEditor()
    assert editor.get_language() is None
    editor.set_language(TextEditor.Language.python())
    assert editor.get_language_name() == "Python"
    editor.set_language(None)
    assert not editor.has_language()
    assert editor.get_language() is None

    diff = TextDiff()
    diff.set_language(TextEditor.Language.cpp())
    assert diff.get_language() is not None
    diff.set_language(None)
    assert diff.get_language() is None
