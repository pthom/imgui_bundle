from dataclasses import dataclass
from typing import List, Optional
import subprocess
import sys
import os

from imgui_bundle import imgui, imgui_color_text_edit as text_edit, imgui_md, ImVec2, immapp


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
    snippet_python: immapp.snippets.SnippetData
    snippet_cpp: immapp.snippets.SnippetData
    demo_apps: List[DemoApp]
    current_app: DemoApp
    demo_python_folder: str
    demo_cpp_folder: str

    def __init__(self, demo_apps: List[DemoApp], demo_python_folder: str, demo_cpp_folder: str):
        self.snippet_cpp = immapp.snippets.SnippetData()
        self.snippet_cpp.displayed_filename = "C++ code"
        self.snippet_cpp.language = immapp.snippets.SnippetLanguage.cpp
        self.snippet_cpp.max_height_in_lines = 22

        self.snippet_python = immapp.snippets.SnippetData()
        self.snippet_python.displayed_filename = "Python code"
        self.snippet_python.language = immapp.snippets.SnippetLanguage.python
        self.snippet_python.max_height_in_lines = 22

        self.demo_apps = demo_apps
        self.demo_python_folder = demo_python_folder
        self.demo_cpp_folder = demo_cpp_folder
        self._set_demo_app(self.demo_apps[0])

    def _demo_python_file_path(self, demo_app: DemoApp) -> str:
        return self.demo_python_folder + "/" + demo_app.demo_file + ".py"

    def _demo_cpp_file_path(self, demo_app: DemoApp) -> str:
        return self.demo_cpp_folder + "/" + demo_app.demo_file + ".cpp"

    def _set_demo_app(self, demo_app: DemoApp):
        self.current_app = demo_app
        self.snippet_cpp.code = _read_code(self._demo_cpp_file_path(demo_app))
        self.snippet_python.code = _read_code(self._demo_python_file_path(demo_app))

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

        immapp.snippets.show_side_by_side_snippets(self.snippet_python, self.snippet_cpp, True, True)
