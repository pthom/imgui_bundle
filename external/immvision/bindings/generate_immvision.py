# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"


def main():
    print("autogenerate_immvision")
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_immvision.cpp"
    output_stub_pyi_file = STUB_DIR + "/immvision.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.use_nanobind()
    options.fn_params_type_replacements.add_replacements([(r"\bImVec2\b", "ImVec2Like"), (r"\bImVec4\b", "ImVec4Like")])

    options.original_signature_flag_show = True
    options.original_location_flag_show = False
    options.namespaces_root = ["ImmVision"]
    options.srcmlcpp_options.functions_api_prefixes = "IMMVISION_API"
    options.srcmlcpp_options.header_filter_acceptable__regex = r"IMMVISION_SERIALIZE_JSON"
    options.python_run_black_formatter = True
    options.fn_exclude_non_api = False

    # Exclude types that are handled by custom nanobind type casters
    # (ImageBuffer <-> numpy, Point/Point2d/Size <-> tuple, Matrix33d <-> list)
    options.class_exclude_by_name__regex = r"^ImageBuffer$|^Point$|^Point2d$|^Size$|^Matrix33d$"

    # Exclude ImageDepth enum and ImageDepthSize function (implementation details)
    options.enum_exclude_by_name__regex = r"^ImageDepth$"
    options.fn_exclude_by_name__regex = r"^ImageDepthSize$"

    def post_process_stub(code: str):
        r = (
            code
            # Fix default values for types handled by type casters
            .replace("ColorMapStatsTypeId()", "ColorMapStatsTypeId.from_full_image")
            .replace("Point2d(-1., -1.)", "(-1., -1.)")
            .replace("Point(-1, -1)", "(-1, -1)")
            .replace("Point2d()", "(0., 0.)")
            .replace("Size()", "(0, 0)")
            .replace("Matrix33d.eye()", "[[1,0,0],[0,1,0],[0,0,1]]")
            .replace("Matrix33d::eye()", "[[1,0,0],[0,1,0],[0,0,1]]")
        )
        return r

    options.postprocess_stub_function = post_process_stub

    generator = litgen.LitgenGenerator(options)
    include_dir = THIS_DIR + "/../immvision/src/immvision/"
    generator.process_cpp_file(include_dir + "immvision_types.h")
    generator.process_cpp_file(include_dir + "image.h")
    generator.process_cpp_file(include_dir + "inspector.h")
    generator.process_cpp_file(include_dir + "gl_texture.h")

    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    main()
