from dataclasses import dataclass
from typing import List, Optional
import subprocess
import sys
import os

from imgui_bundle import imgui, imgui_color_text_edit as text_edit, imgui_md, ImVec2


def _read_code(filepath: str) -> str:
    if os.path.isfile(filepath):
        with open(filepath) as f:
            code = f.read()
            return code
    else:
        return ""


@dataclass
class DemoApp:
    demo_file: str
    explanation: str


class DemoAppTable:
    editor_python: text_edit.TextEditor
    editor_cpp: text_edit.TextEditor
    demo_apps: List[DemoApp]
    current_app: DemoApp
    demo_python_folder: str
    demo_cpp_folder: str

    def __init__(self, demo_apps: List[DemoApp], demo_python_folder: str, demo_cpp_folder: str, idx_initial_app: int = 0):
        self.editor_python = text_edit.TextEditor()
        self.editor_python.set_language_definition(text_edit.TextEditor.LanguageDefinition.python())
        self.editor_cpp = text_edit.TextEditor()
        self.editor_cpp.set_language_definition(text_edit.TextEditor.LanguageDefinition.c_plus_plus())
        self.demo_apps = demo_apps
        self.demo_python_folder = demo_python_folder
        self.demo_cpp_folder = demo_cpp_folder
        self._set_demo_app(self.demo_apps[idx_initial_app])

    def _demo_python_file_path(self, demo_app: DemoApp) -> str:
        return self.demo_python_folder + "/" + demo_app.demo_file + ".py"

    def _demo_cpp_file_path(self, demo_app: DemoApp) -> str:
        return self.demo_cpp_folder + "/" + demo_app.demo_file + ".cpp"

    def _set_demo_app(self, demo_app: DemoApp):
        self.current_app = demo_app
        self.editor_python.set_text(_read_code(self._demo_python_file_path(demo_app)))
        self.editor_cpp.set_text(_read_code(self._demo_cpp_file_path(demo_app)))

    def gui(self):
        table_flags = imgui.TableFlags_.row_bg | imgui.TableFlags_.borders | imgui.TableFlags_.resizable
        nb_columns = 3
        if imgui.begin_table("Apps", nb_columns, table_flags):
            imgui.table_setup_column("Demo")
            imgui.table_setup_column("Info")
            imgui.table_setup_column("Action")
            # imgui.table_headers_row()

            for demo_app in self.demo_apps:
                imgui.push_id(demo_app.demo_file)
                imgui.table_next_row()

                imgui.table_next_column()
                imgui.text(demo_app.demo_file + ".py")
                imgui.table_next_column()

                imgui_md.render_unindented(demo_app.explanation)

                if len(demo_app.demo_file) > 0:
                    imgui.table_next_column()
                    if imgui.button("View code"):
                        self._set_demo_app(demo_app)

                    imgui.same_line()

                    if imgui.button("Run"):
                        subprocess.Popen([sys.executable, self._demo_python_file_path(demo_app)])

                imgui.pop_id()

            imgui.end_table()

        imgui.new_line()
        imgui.text(f"Code for {self.current_app.demo_file}")
        imgui.push_font(imgui_md.get_code_font())

        has_both_languages = len(self.editor_python.get_text()) > 0 and len(self.editor_cpp.get_text()) > 0
        if has_both_languages:
            editor_size = ImVec2(imgui.get_window_width() / 2.03, 0.)
        else:
            editor_size = ImVec2(imgui.get_window_width(), 0.)

        if len(self.editor_python.get_text()) > 0:
            imgui.begin_group()
            imgui.text("Python code")
            self.editor_python.render("Python code", editor_size)
            imgui.end_group()
        if has_both_languages:
            imgui.same_line()
        if len(self.editor_cpp.get_text()) > 0:
            imgui.begin_group()
            imgui.text("C++ code")
            self.editor_cpp.render("C++ code", editor_size)
            imgui.end_group()
        imgui.pop_font()
