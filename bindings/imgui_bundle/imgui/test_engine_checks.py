from imgui_bundle._imgui_bundle import imgui as imgui  # type: ignore
import traceback


def _check(result: bool, backtrace_nb: int) -> None:
    traceback_info = traceback.extract_stack()
    caller_info = traceback_info[-backtrace_nb]
    filename, line_num, func_name, line_code = caller_info

    imgui.test_engine.check(
        filename,
        func_name,
        line_num,
        imgui.test_engine.TestCheckFlags_.none,
        result,
        line_code,
    )


def CHECK(result: bool) -> None:
    _check(result, 3)


def check_no_ret(result: bool) -> None:
    """
    Not implemented, because I did not understand the intended behavior

    #define IM_CHECK_OP(_LHS, _RHS, _OP, _RETURN)                       \
        do                                                              \
        {                                                               \
            ...                                                         \
            if (ImGuiTestEngine_Check(__FILE__, __func__, __LINE__, ImGuiTestCheckFlags_None, __res, expr_buf.c_str())) \
                IM_ASSERT(__res);                                       \
            if (_RETURN && !__res)                                      \
                return;                                                 \
        } while (0)
    """
    raise NotImplementedError()
