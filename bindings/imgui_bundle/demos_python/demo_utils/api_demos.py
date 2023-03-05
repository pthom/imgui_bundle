import os
from typing import Callable, Dict
from imgui_bundle import immapp, imgui, ImVec2, imgui_md, hello_imgui
from imgui_bundle.demos_python.demo_utils.functional_utils import memoize
from imgui_bundle import imgui_color_text_edit as text_edit


GuiFunction = Callable[[], None]


def main_python_package_folder() -> str:
    this_dir = os.path.dirname(__file__)
    this_dir = this_dir.replace("\\", "/")

    items = this_dir.split("/")

    for n in reversed(range(len(items))):
        parent_folder = "/".join(items[:n])
        if os.path.isfile(parent_folder + "/hello_imgui.pyi"):
            return parent_folder

    raise Exception("Cannot find main python package!")


def demos_assets_folder() -> str:
    r = main_python_package_folder() + "/demos_assets"
    return r


def demos_cpp_folder() -> str:
    return main_python_package_folder() + "/demos_cpp"


def demos_python_folder() -> str:
    return main_python_package_folder() + "/demos_python"


def markdown_doc_folder() -> str:
    return main_python_package_folder() + "/doc/imgui_bundle_demo_parts"


def set_hello_imgui_demo_assets_folder():
    hello_imgui.set_assets_folder(demos_assets_folder())


def show_python_vs_cpp_code(python_code: str, cpp_code: str, nb_lines: int = 0):
    imgui.push_id(python_code)

    snippet_cpp: text_edit.SnippetData = immapp.snippets.SnippetData()
    snippet_cpp.code = cpp_code
    snippet_cpp.displayed_filename = "C++ code"
    snippet_cpp.height_in_lines = nb_lines

    snippet_python: text_edit.SnippetData = immapp.snippets.SnippetData()
    snippet_python.code = python_code
    snippet_python.displayed_filename = "Python code"
    snippet_python.height_in_lines = nb_lines

    immapp.snippets.show_side_by_side_snippets(snippet_python, snippet_cpp)

    imgui.pop_id()


def show_python_vs_cpp_and_run(python_gui_function, cpp_code: str, nb_lines: int = 0) -> None:
    import inspect

    python_code = inspect.getsource(python_gui_function)
    show_python_vs_cpp_code(python_code, cpp_code, nb_lines)
    python_gui_function()


def show_python_vs_cpp_file(demo_file_path: str, nb_lines: int = 0) -> None:
    cpp_code = read_cpp_code(demo_file_path)
    python_code = read_python_code(demo_file_path)
    show_python_vs_cpp_code(python_code, cpp_code, nb_lines)


def show_markdown_file(doc_filename: str) -> None:
    code = read_markdown_code(doc_filename)
    imgui_md.render_unindented(code)


@memoize
def read_code(filename: str) -> str:
    if not os.path.isfile(filename):
        return ""
    with open(filename, encoding="utf8") as f:
        r = f.read()
        return r


def read_cpp_code(demo_file_path: str) -> str:
    file_abs = demos_cpp_folder() + "/" + demo_file_path + ".cpp"
    code = read_code(file_abs)
    return code


def read_python_code(demo_file_path: str) -> str:
    file_abs = demos_python_folder() + "/" + demo_file_path + ".py"
    code = read_code(file_abs)
    return code


def read_markdown_code(doc_filename: str) -> str:
    doc_file = markdown_doc_folder() + "/" + doc_filename + ".adoc.md"
    r = read_code(doc_file)
    return r
