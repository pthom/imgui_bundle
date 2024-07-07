from dataclasses import dataclass
from typing import List
import subprocess
import sys
import os

from imgui_bundle import imgui, imgui_md, immapp, hello_imgui, ImVec2
from typing import Callable



def _read_code(filepath: str) -> str:
    if os.path.isfile(filepath):
        with open(filepath, encoding="utf8") as f:
            code = f.read()
            return code
    else:
        return ""


@dataclass
class DemoApp:
    demo_file: str
    explanation: str
    is_python_backend_demo: bool = False


class DemoAppTable:
    snippet_python: immapp.snippets.SnippetData  # type: ignore
    snippet_cpp: immapp.snippets.SnippetData  # type: ignore
    demo_apps: List[DemoApp]
    current_app: DemoApp
    demo_python_folder: str
    demo_cpp_folder: str
    demo_python_backend_folder: str

    def __init__(
            self,
            demo_apps: List[DemoApp],
            demo_python_folder: str,
            demo_cpp_folder: str,
            demo_python_backend_folder: str,
    ):
        self.snippet_cpp = immapp.snippets.SnippetData()
        self.snippet_cpp.displayed_filename = "C++ code"
        self.snippet_cpp.language = immapp.snippets.SnippetLanguage.cpp
        self.snippet_cpp.max_height_in_lines = 30

        self.snippet_python = immapp.snippets.SnippetData()
        self.snippet_python.displayed_filename = "Python code"
        self.snippet_python.language = immapp.snippets.SnippetLanguage.python
        self.snippet_python.max_height_in_lines = 30

        self.demo_apps = demo_apps
        self.demo_python_folder = demo_python_folder
        self.demo_cpp_folder = demo_cpp_folder
        self.demo_python_backend_folder = demo_python_backend_folder
        self._set_demo_app(self.demo_apps[0])

    def _demo_python_file_path(self, demo_app: DemoApp) -> str:
        folder = self.demo_python_backend_folder if demo_app.is_python_backend_demo else self.demo_python_folder
        return folder + "/" + demo_app.demo_file + ".py"

    def _demo_cpp_file_path(self, demo_app: DemoApp) -> str:
        return self.demo_cpp_folder + "/" + demo_app.demo_file + ".cpp"

    def _set_demo_app(self, demo_app: DemoApp):
        self.current_app = demo_app
        self.snippet_cpp.code = _read_code(self._demo_cpp_file_path(demo_app))
        self.snippet_python.code = _read_code(self._demo_python_file_path(demo_app))

    @immapp.static(
        shall_scroll_down=False, shall_scroll_up=False,
        scroll_delta=0.0, scroll_current=0.0, child_size=(0.0, 0.0))
    def display_demo_app_table_with_scroll_buttons(self, window_name: str, window_size: ImVec2, gui: Callable):
        statics = DemoAppTable.display_demo_app_table_with_scroll_buttons

        imgui.begin_child(window_name, window_size)
        statics.scroll_current = imgui.get_scroll_y()

        if statics.shall_scroll_up:
            imgui.set_scroll_y(statics.scroll_current - statics.scroll_delta)
            statics.shall_scroll_up = False

        if statics.shall_scroll_down:
            imgui.set_scroll_y(statics.scroll_current + statics.scroll_delta)
            statics.shall_scroll_down = False

        gui()

        statics.child_size = imgui.get_cursor_pos()

        imgui.end_child()

        # Scroll buttons
        statics.scroll_delta = imgui.get_item_rect_size()[1] - hello_imgui.em_size(0.5)
        imgui.new_line()
        imgui.same_line(imgui.get_item_rect_size().x - hello_imgui.em_size(3.0))

        imgui.begin_disabled(statics.scroll_current == 0.0)
        if imgui.arrow_button("##up", imgui.Dir.up):
            statics.shall_scroll_up = True
        imgui.end_disabled()

        imgui.same_line()
        imgui.begin_disabled(statics.scroll_current + statics.scroll_delta > statics.child_size[1] - imgui.get_item_rect_size()[1])
        if imgui.arrow_button("##down", imgui.Dir.down):
            statics.shall_scroll_down = True
        imgui.end_disabled()

        imgui.same_line()
        imgui.set_cursor_pos_x(0.0)

    def gui(self):

        def fn_table_gui():
            table_flags = (
                imgui.TableFlags_.row_bg
                | imgui.TableFlags_.borders
                | imgui.TableFlags_.resizable
                | imgui.TableFlags_.sizing_stretch_same
            )
            nb_columns = 3
            if imgui.begin_table("Apps", nb_columns, table_flags):
                imgui.table_setup_column("Demo", 0, 0.15)
                imgui.table_setup_column("Info", 0, 0.6)
                imgui.table_setup_column("Action", 0, 0.1)
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
                            subprocess.Popen(
                                [sys.executable, self._demo_python_file_path(demo_app)]
                            )

                    imgui.pop_id()
                imgui.end_table()

        self.display_demo_app_table_with_scroll_buttons(
            "DemoAppTable", hello_imgui.em_to_vec2(0.0, 9.6), fn_table_gui)
        imgui_md.render("**Code for " + self.current_app.demo_file + "**")
        immapp.snippets.show_side_by_side_snippets(
            self.snippet_python, self.snippet_cpp, True, True
        )

