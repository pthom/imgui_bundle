import os

import litgen


_THIS_DIR = os.path.dirname(__file__)
BUNDLE_DIR = os.path.realpath(_THIS_DIR + "/..")
CPP_HEADERS_DIR = BUNDLE_DIR + "/external/immapp"
CPP_GENERATED_PYBIND_DIR = BUNDLE_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def autogenerate_immapp():
    print("autogenerate_immapp")
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_immapp_cpp.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/immapp/immapp_cpp.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.namespace_root__regex = "ImmApp"
    options.python_run_black_formatter = True
    options.srcmlcpp_options.ignored_warnings.append(
        "Block elements of type decl_stmt are not supported in python conversion"
    )

    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_file(CPP_HEADERS_DIR + "/immapp.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/runner.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/utils.h")

    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    autogenerate_immapp()
