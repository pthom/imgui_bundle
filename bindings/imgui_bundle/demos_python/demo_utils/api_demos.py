import os
from typing import Callable, Dict
from imgui_bundle import immapp, imgui, imgui_color_text_edit, ImVec2, imgui_md
from imgui_bundle.demos_python.demo_utils import code_str_utils
from imgui_bundle.demos_python.demo_utils.functional_utils import memoize


GuiFunction = Callable[[], None]
TextEditor = imgui_color_text_edit.TextEditor


def demos_assets_folder() -> str:
    import os

    this_dir = os.path.dirname(__file__)
    r = os.path.abspath(f"{this_dir}/../assets")
    return r


@immapp.static(editors={})
def show_code_editor(code: str, is_cpp: bool, flag_half_width: bool, nb_lines: int = 0):
    static = show_code_editor
    editors: Dict[str, TextEditor] = static.editors

    if code not in editors.keys():
        editors[code] = TextEditor()
        if is_cpp:
            editors[code].set_language_definition(TextEditor.LanguageDefinition.c_plus_plus())
        else:
            editors[code].set_language_definition(TextEditor.LanguageDefinition.python())
        editors[code].set_text(code)

    if nb_lines == 0:
        nb_lines = len(editors[code].get_text().split("\n"))
    if flag_half_width:
        editor_size = ImVec2(imgui.get_window_width() / 2.0 - 20.0, immapp.em_size() * 1.025 * nb_lines)
    else:
        editor_size = ImVec2(imgui.get_window_width() - 20.0, immapp.em_size() * 1.025 * nb_lines)
    editor_title = "cpp" if is_cpp else "python"

    imgui.push_font(imgui_md.get_code_font())
    editors[code].render(f"##{editor_title}", editor_size)
    imgui.pop_font()


def show_python_vs_cpp_code(python_code: str, cpp_code: str, nb_lines: int = 0):
    imgui.push_id(python_code)

    flag_half_width = len(python_code) > 0 and len(cpp_code) > 0

    if len(cpp_code) > 0:
        imgui.begin_group()
        imgui.text("C++ code")
        show_code_editor(cpp_code, is_cpp=True, flag_half_width=flag_half_width, nb_lines=nb_lines)
        imgui.end_group()

        if len(python_code) > 0:
            imgui.same_line()

    if len(python_code) > 0:
        imgui.begin_group()
        imgui.text("Python code")
        show_code_editor(python_code, is_cpp=False, flag_half_width=flag_half_width, nb_lines=nb_lines)
        imgui.end_group()

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


def render_md_unindented(md_str: str, flag_strip_empty_lines: bool = True) -> None:
    s = code_str_utils.unindent_code(md_str, flag_strip_empty_lines=flag_strip_empty_lines)
    imgui_md.render(s)


def main_python_package_folder() -> str:
    this_dir = os.path.dirname(__file__)
    this_dir = this_dir.replace("\\", "/")

    items = this_dir.split("/")

    for n in reversed(range(len(items))):
        parent_folder = "/".join(items[:n])
        if os.path.isfile(parent_folder + "/hello_imgui.pyi"):
            return parent_folder

    raise Exception("Cannot find main python package!")


def demos_cpp_folder() -> str:
    return main_python_package_folder() + "/demos_cpp"


def demos_python_folder() -> str:
    return main_python_package_folder() + "/demos_python"


def read_code(filename: str):
    with open(filename) as f:
        r = f.read()
        return r


@memoize
def read_cpp_code(demo_file_path: str):
    file_abs = demos_cpp_folder() + "/" + demo_file_path + ".cpp"
    if not os.path.isfile(file_abs):
        return ""
    code = read_code(file_abs)
    return code


@memoize
def read_python_code(demo_file_path: str):
    file_abs = demos_python_folder() + "/" + demo_file_path + ".py"
    if not os.path.isfile(file_abs):
        return ""
    code = read_code(file_abs)
    return code
