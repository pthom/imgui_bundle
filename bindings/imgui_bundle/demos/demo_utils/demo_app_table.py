from typing import List
import subprocess
import sys

from imgui_bundle import imgui, imgui_color_text_edit as text_edit, imgui_md
from imgui_bundle.demos.demo_utils.code_str_utils import unindent_code


class DemoApp:
    python_file: str
    explanation: str

    def __init__(self, python_file: str, explanation: str):
        self.python_file = python_file
        self.explanation = unindent_code(explanation, flag_strip_empty_lines=True)


class DemoAppTable:
    editor: text_edit.TextEditor
    demo_apps: List[DemoApp]
    current_app: DemoApp
    demo_folder: str

    def __init__(self,
                 demo_apps: List[DemoApp],
                 demo_folder: str,
                 idx_initial_app: int = 0):
        self.editor = text_edit.TextEditor()
        self.editor.set_language_definition(text_edit.TextEditor.LanguageDefinition.python())
        self.demo_apps = demo_apps
        self.demo_folder = demo_folder
        self._set_demo_app(self.demo_apps[idx_initial_app])

    def _demo_file_path(self, demo_file: str) -> str:
        return self.demo_folder + "/" + demo_file

    def _set_demo_app(self, demo_app: DemoApp):
        self.current_app = demo_app
        with open(self._demo_file_path(demo_app.python_file)) as f:
            code = f.read()
        self.editor.set_text(code)

    def gui(self):
        table_flags = imgui.TableFlags_.row_bg | imgui.TableFlags_.borders | imgui.TableFlags_.resizable
        nb_columns = 3
        if imgui.begin_table("Apps", nb_columns, table_flags):
            imgui.table_setup_column("Demo")
            imgui.table_setup_column("Info")
            imgui.table_setup_column("Action")
            # imgui.table_headers_row()

            for demo_app in self.demo_apps:
                imgui.push_id(demo_app.python_file)
                imgui.table_next_row()

                imgui.table_next_column()
                imgui.text(demo_app.python_file)
                imgui.table_next_column()

                cursor_pos = imgui.get_cursor_pos()
                cursor_pos.y -= imgui.get_font_size()
                imgui.set_cursor_pos(cursor_pos)
                imgui_md.render(demo_app.explanation)

                if len(demo_app.python_file) > 0:
                    imgui.table_next_column()
                    if imgui.button("View code"):
                        self._set_demo_app(demo_app)

                    imgui.same_line()

                    if imgui.button("Run"):
                        subprocess.Popen([sys.executable, self._demo_file_path(demo_app.python_file)])

                imgui.pop_id()

            imgui.end_table()

        imgui.new_line()
        imgui.text(f"Code for {self.current_app.python_file}")
        self.editor.render("Code")
