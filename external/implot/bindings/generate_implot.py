# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen
from litgen_options_implot import litgen_options_implot


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../implot"


def autogenerate_implot():
    print("autogenerate_implot")
    input_cpp_header = CPP_HEADERS_DIR + "/implot.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_implot.cpp"
    output_stub_pyi_file = STUB_DIR + "/implot/__init__.pyi"

    # Configure options
    options = litgen_options_implot()
    options.srcmlcpp_options.flag_show_progress = True

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


def autogenerate_implot_internal() -> None:
    print("autogenerate_implot_internal")
    options = litgen_options_implot()
    options.srcmlcpp_options.flag_show_progress = True
    options.python_run_black_formatter = False

    options.fn_exclude_by_name__regex += "|" + "|".join(
        [
            "^ImMinMaxArray$",
            "^ImMinArray$",
            "^ImMaxArray$",
            "^ImSum$",
            "^FormatDate$",
            "^FormatDateTime$",
            "^LabelAxisValue$",
            "^MkGmtTime$",
            "^GetGmtTime$",
            "^MkLocTime$",
            "^GetLocTime$",
            "^FormatTime$",
            "^Formatter_Default$",
            "^Formatter_Logit$",
            "^Formatter_Time$",
        ]
    )
    options.member_exclude_by_name__regex += "|^Formatter$|^Locator$"
    options.member_exclude_by_type__regex += "|^ImPlotTransform$|^ImPlotFormatter$|^tm$"
    options.fn_force_lambda__regex += "|^GetText$"

    options.srcmlcpp_options.ignored_warning_parts.append("Excluding template type ImVector")

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=CPP_HEADERS_DIR + "/implot_internal.h",
        output_cpp_pydef_file=PYDEF_DIR + "/pybind_implot_internal.cpp",
        output_stub_pyi_file=STUB_DIR + "/implot/internal.pyi",
    )


def sandbox():
    code = """
    """
    options = litgen_options_implot()
    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_code(code, "file")
    print(generator.stub_code())


def main():
    autogenerate_implot()
    autogenerate_implot_internal()
    # sandbox()


if __name__ == "__main__":
    main()
