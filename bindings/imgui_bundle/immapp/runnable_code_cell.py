"""show_runnable_code_cell: a Jupyter notebook like code cell

* Displays an editable code cell
* A Run button
* An indication (*) whether the code was modified since it was last run.
* The result of the last run is displayed below the code cell
  (you can provide a custom renderer for the result)
* If the result is a function, it is called every frame: the cell becomes a live GUI

This is very much a work in progress.
"""

import ast
import inspect
import sys
import io
from typing import Any, Callable

from imgui_bundle import immapp, rich_md, imgui, imgui_ctx, hello_imgui, implot, ImVec2
import textwrap
from dataclasses import dataclass


class _NoResult:
    pass


_NoResultValue = _NoResult()



ResultRenderer = Callable[[Any], None]


def _default_result_renderer(result: Any) -> None:
    if inspect.isfunction(result):
        result()  # a live GUI function
        return
    as_string = str(result)
    md_string = "```\n" + as_string + "\n```"
    rich_md.render(md_string)



class _CaptureStdout(list[str]):
    def __enter__(self) -> "_CaptureStdout":
        self._stdout = sys.stdout
        sys.stdout = self._stringio = io.StringIO()
        return self

    def __exit__(self, *args: Any) -> None:
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout


# Shared by all cells, and kept between runs (like Jupyter)
_cells_namespace: dict[str, Any] = {}


def _render_and_recover_on_error(result_renderer: ResultRenderer, result: Any) -> Exception | None:
    """Calls result_renderer(result). If it raises, closes what it left open in ImGui and ImPlot and returns the exception"""
    state = imgui.internal.ErrorRecoveryState()
    imgui.internal.error_recovery_store_state(state)
    try:
        result_renderer(result)
        return None
    except Exception as e:
        # A plot left open would assert at the next begin_plot
        if implot.get_current_context() is not None and implot.internal.get_current_plot() is not None:
            implot.end_plot()
        # Close the ImGui stacks (groups, ids, styles, ...) without asserting
        io = imgui.get_io()
        enable_assert = io.config_error_recovery_enable_assert
        io.config_error_recovery_enable_assert = False
        imgui.internal.error_recovery_try_to_recover_state(state)
        io.config_error_recovery_enable_assert = enable_assert
        return e


def _execute_and_capture_last_expr(code: str) -> Any | _NoResult:
    with _CaptureStdout():
        code = textwrap.dedent(code).strip()  # De-indent and strip code
        try:
            tree = ast.parse(code, "<cell>")
            # If the last statement is an expression, evaluate it separately to return its value
            last_expr = None
            if tree.body and isinstance(tree.body[-1], ast.Expr):
                last_expr = ast.Expression(tree.body.pop().value)
            exec(compile(tree, "<cell>", "exec"), _cells_namespace)
            if last_expr is None:
                return _NoResult()
            return eval(compile(last_expr, "<cell>", "eval"), _cells_namespace)
        except Exception as e:
            return f"Error:\n{e}"


@dataclass
class RunnableCodeCellResult:
    code: str = ""
    last_run_code: str = ""
    was_last_edited_code_ran: bool = False # simply indicates if last_run_code == code
    result: Any = _NoResultValue
    was_just_run: bool = False


def show_runnable_code_cell(label_id: str, code: str = "", result_renderer: ResultRenderer | None = None) -> RunnableCodeCellResult:
    statics = show_runnable_code_cell

    @dataclass
    class CodeAndResult:
        snippet_data: immapp.snippets.SnippetData
        result: Any
        last_ran_code: str

    if not hasattr(statics, "s_code_cells"):
        statics.s_code_cells: dict[str, CodeAndResult] = {}  # type: ignore

    if label_id not in statics.s_code_cells:
        snippet_data = immapp.snippets.SnippetData()
        snippet_data.code = code
        snippet_data.height_in_lines = code.count("\n")
        snippet_data.palette = immapp.snippets.SnippetTheme.dark
        snippet_data.read_only = False  # the cell's code is edited, then run
        statics.s_code_cells[label_id] = CodeAndResult(snippet_data, _NoResult(), "")

    code_and_result = statics.s_code_cells[label_id]
    runnnable_code_cell_result = RunnableCodeCellResult()

    with imgui_ctx.push_id(label_id):
        original_cur_pos = imgui.get_cursor_screen_pos()
        visible_label = label_id if "##" not in label_id else label_id.split("##")[0]
        imgui.separator_text(visible_label)

        # Add "Run" button at the end of the separator line
        cur_pos_after_separator = imgui.get_cursor_screen_pos()
        x_end = imgui.get_item_rect_max().x
        x_end = x_end - hello_imgui.em_size(3.5)
        imgui.set_cursor_screen_pos(ImVec2(x_end, original_cur_pos.y))
        if imgui.button("Run"):
            code_and_result.result = _execute_and_capture_last_expr(code_and_result.snippet_data.code)
            code_and_result.last_ran_code = code_and_result.snippet_data.code
            runnnable_code_cell_result.was_just_run = True
        if code_and_result.last_ran_code != code_and_result.snippet_data.code:
            imgui.same_line()
            imgui.text("*")
        imgui.set_cursor_screen_pos(cur_pos_after_separator)

        immapp.snippets.show_editable_code_snippet(label_id, code_and_result.snippet_data)

        runnnable_code_cell_result.code = code_and_result.snippet_data.code
        runnnable_code_cell_result.last_run_code = code_and_result.last_ran_code
        runnnable_code_cell_result.result = code_and_result.result
        runnnable_code_cell_result.was_last_edited_code_ran = code_and_result.last_ran_code == code_and_result.snippet_data.code

        if not isinstance(code_and_result.result, _NoResult):
            if result_renderer is None:
                result_renderer = _default_result_renderer
            error = _render_and_recover_on_error(result_renderer, code_and_result.result)
            if error is not None:
                code_and_result.result = f"Error:\n{error}"  # shown from the next frame, until the next run

        imgui.new_line()

    return runnnable_code_cell_result
