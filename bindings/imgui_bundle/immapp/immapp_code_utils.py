from imgui_bundle import immapp, imgui_md

import inspect
import json
from typing import Any


SnippetData = immapp.snippets.SnippetData


def show_python_code(
        python_object: object,  # can be a class, function, module, etc.
        read_only: bool = True,
        height_in_lines: int | None = None,
        max_height_in_lines: int | None = None,
        show_cursor_position: bool | None = None,
        de_indent_code: bool | None = None,
        show_copy_button: bool | None = None,
        palette: immapp.snippets.SnippetTheme | None = immapp.snippets.SnippetTheme.mariana,
        border: bool | None = None,
    ) -> None:
    """Render the code of an object as a markdown code block"""

    statics = show_python_code
    if not hasattr(statics, "_ALL_PYTHON_SNIPPETS"):
        statics._ALL_PYTHON_SNIPPETS: dict[object, SnippetData] = {}

    if python_object not in statics._ALL_PYTHON_SNIPPETS:
        snippet_data = SnippetData()

        snippet_data.displayed_filename = str(python_object)
        snippet_data.code = inspect.getsource(python_object)
        snippet_data.language = immapp.snippets.SnippetLanguage.python

        if read_only is not None:
            snippet_data.read_only = read_only
        if height_in_lines is not None:
            snippet_data.height_in_lines = height_in_lines
        if max_height_in_lines is not None:
            snippet_data.max_height_in_lines = max_height_in_lines
        if show_cursor_position is not None:
            snippet_data.show_cursor_position = show_cursor_position
        if de_indent_code is not None:
            snippet_data.de_indent_code = de_indent_code
        if show_copy_button is not None:
            snippet_data.show_copy_button = show_copy_button
        if palette is not None:
            snippet_data.palette = palette
        if border is not None:
            snippet_data.border = border

        statics._ALL_PYTHON_SNIPPETS[python_object] = snippet_data

    cached_snippet_data = statics._ALL_PYTHON_SNIPPETS[python_object]
    immapp.snippets.show_code_snippet(cached_snippet_data)


def _compact_json(data, indent=4):
    def _compact_list(lst, indent_level):
        compacted = json.dumps(lst)
        if len(compacted) <= 80:
            return compacted
        return json.dumps(lst, indent=indent, separators=(',', ': '))

    def _compact_dict(dct, indent_level):
        items = []
        for key, value in dct.items():
            key_str = json.dumps(key) + ': '
            value_str = (
                _compact_list(value, indent_level + 1)
                if isinstance(value, list)
                else json.dumps(value, indent=indent, separators=(',', ': '))
            )
            items.append('\n' + ' ' * indent_level * indent + key_str + value_str)
        return '{' + ','.join(items) + '\n' + ' ' * (indent_level - 1) * indent + '}'

    return _compact_dict(data, 1)


def show_json_dict(json_dict: dict[str, Any]):
    """Render a json dict as a markdown code block"""
    md_string = "```\n" +  _compact_json(json_dict, indent=4) + "\n```"
    imgui_md.render(md_string)
