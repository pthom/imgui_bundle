import os

import litgen


_THIS_DIR = os.path.dirname(__file__)
BUNDLE_DIR = os.path.realpath(_THIS_DIR + "/..")
CPP_HEADERS_DIR = BUNDLE_DIR + "/external/immvision/immvision/src_all_in_one/immvision"
CPP_GENERATED_PYBIND_DIR = BUNDLE_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def autogenerate_immvision():
    print("autogenerate_immvision")
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_immvision.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/immvision.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.original_signature_flag_show = True
    options.original_location_flag_show = True
    options.namespace_root__regex = "ImmVision"
    options.srcmlcpp_options.functions_api_prefixes = "IMMVISION_API"
    options.python_run_black_formatter = True

    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_file(CPP_HEADERS_DIR + "/immvision.h")

    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    autogenerate_immvision()
