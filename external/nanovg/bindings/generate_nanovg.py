# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os
import string

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"


def main():
    print("autogenerate_nanovg")
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_nanovg.cpp"
    output_stub_pyi_file = STUB_DIR + "/nanovg.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.srcmlcpp_options.header_filter_acceptable__regex += "|IMGUI_BUNDLE_WITH_NANOVG"
    options.original_signature_flag_show = True
    options.type_replacements.add_last_replacement("unsigned char", "UChar")
    options.var_names_replacements.add_last_replacement("^NVG_", "")
    options.function_names_replacements.add_last_replacement("^nvgcpp_", "")
    options.function_names_replacements.add_last_replacement("^nvg", "")
    options.function_names_replacements.add_last_replacement("^RGBAf$", "rgba_f")
    options.function_names_replacements.add_last_replacement("^RGBf$", "rgb_f")
    options.function_names_replacements.add_last_replacement("ImGui", "Imgui")
    options.class_exclude_by_name__regex = "^NVGcolor$"  # contains a union...

    # The entire nvgText API is oriented around C style strings, and needs adaptations
    options.fn_exclude_by_name__regex = r"^nvgText|^nvgImageSize$"

    for letter in string.ascii_lowercase:
        options.type_replacements.add_last_replacement(
            "NVG" + letter, letter.upper()
        )

    options.srcmlcpp_options.ignored_warning_parts.append("C style function pointers are poorly supported")

    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_file(THIS_DIR + "/../nanovg/src/nanovg.h")
    generator.process_cpp_file(THIS_DIR + "/../nvg_imgui/nvg_imgui.h")
    generator.process_cpp_file(THIS_DIR + "/../nvg_imgui/nvg_cpp_text.h")
    generator.write_generated_code(output_cpp_pydef_file, output_stub_pyi_file)


if __name__ == "__main__":
    main()
