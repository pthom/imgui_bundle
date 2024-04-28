# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../immapp"


def main():
    print("autogenerate_immapp")
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_immapp_cpp.cpp"
    output_stub_pyi_file = STUB_DIR + "/immapp/immapp_cpp.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.namespaces_root = ["ImmApp"]
    options.python_run_black_formatter = True
    options.srcmlcpp_options.ignored_warnings.append(
        "Block elements of type decl_stmt are not supported in python conversion"
    )
    options.srcmlcpp_options.header_filter_acceptable__regex += "|IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR"
    options.srcmlcpp_options.ignored_warning_parts += ["unhandled tag endif", "unhandled tag ifdef"]

    options.fn_return_force_policy_reference_for_references__regex = r".*"
    options.fn_return_force_policy_reference_for_pointers__regex = r".*"

    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_file(CPP_HEADERS_DIR + "/immapp.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/immapp_widgets.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/runner.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/clock.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/code_utils.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/snippets.h")

    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    main()
