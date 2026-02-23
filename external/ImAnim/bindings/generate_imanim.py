# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen
from codemanip import code_utils


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../ImAnim"


def main():
    print("autogenerate_imanim")
    input_cpp_header = CPP_HEADERS_DIR + "/im_anim.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imanim.cpp"
    output_stub_pyi_file = STUB_DIR + "/im_anim.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.use_nanobind()

    options.srcmlcpp_options.header_filter_acceptable__regex += "|IMGUI_BUNDLE_PYTHON_API"

    options.original_signature_flag_show = True

    options.fn_params_output_modifiable_immutable_to_return__regex = r".*"

    # Standard ImVec replacements for function parameters
    options.fn_params_type_replacements.add_replacements([
        (r"\bImVec2\b", "ImVec2Like"),
        (r"\bImVec4\b", "ImVec4Like")
    ])

    # Remove iam_ prefix from function names (keep underscore naming style)
    options.function_names_replacements.add_last_replacement("^iam_", "")
    options.var_names_replacements.add_last_replacement("^iam_", "")
    options.function_names_replacements.add_last_replacement("^ImAnim", "")

    # Remove iam_ prefix from type names (enums, classes, structs)
    options.type_replacements.add_last_replacement(r"^iam_", "")

    options.fn_params_exclude_types__regex = code_utils.join_string_by_pipe_char([
        r"void\s*\*",             # void* user data
    ])
    options.fn_params_exclude_names__regex = code_utils.join_string_by_pipe_char([
        r"bezier4",             # a float* which expect 4 float, without any type information, so we can't generate a proper binding for it
    ])

    # ==========================================
    # Exclude bloat features from Python bindings
    # (see _plans/imanim_trim_bindings__plan.md)
    # ==========================================

    options.fn_exclude_by_name__regex = code_utils.join_string_by_pipe_char([
        # Previously excluded
        r"iam_transform_to_matrix",
        # Profiler, drag feedback
        r"iam_profiler_.*",
        r"iam_drag_.*",
        # Tween variants: relative, resolved, per-axis
        r"iam_tween_.*_(rel$|resolved|per_axis)",
        # Anchor size (only used by relative tweens)
        r"iam_anchor_size",
        # Motion paths, arc-length, path morphing
        r"iam_(bezier_quadratic|bezier_cubic|catmull_rom|path_|tween_path|get_morph_blend).*",
        # Text along paths, text stagger
        r"iam_text_(path|stagger).*",
        # Quad transform helpers
        r"iam_(transform_quad|make_glyph_quad)",
        # Noise
        r"iam_(noise|smooth_noise)_.*",
        # Style interpolation
        r"iam_style_.*",
        # Gradient, transform interpolation
        r"iam_(gradient_lerp|tween_gradient|transform_lerp|tween_transform|transform_from_matrix)",
        # Layering (keep iam_get_blended_color, exclude the rest)
        r"iam_layer_.*",
        r"iam_get_blended_(float|vec[24]|int)",
        # Clip persistence
        r"iam_clip_(save|load)",
        # Variation helpers (all 60+)
        r"iam_var(f|i|v2|v4|c)_.*",
        # Demo windows (keep only basics)
        r"ImAnim(Demo|Doc|Usecase)Window",
    ])

    options.class_exclude_by_name__regex = code_utils.join_string_by_pipe_char([
        r"iam_(drag_opts|drag_feedback|ease_per_axis)",
        r"iam_(morph_opts|text_path_opts|text_stagger_opts|noise_opts)",
        r"iam_(gradient|transform|path)$",
        r"iam_variation_(float|int|vec[24]|color)",
    ])

    options.enum_exclude_by_name__regex = code_utils.join_string_by_pipe_char([
        r"iam_(anchor_space|path_segment_type|noise_type|rotation_mode|variation_mode)",
        r"iam_text_(path_align|stagger_effect)",
    ])

    options.member_exclude_by_name_and_class__regex = {
        "iam_clip": code_utils.join_string_by_pipe_char([
            r"key_.*_(var|rel|spring)",
            r"set_(duration|delay|timescale)_var",
            r"(seq|par)_(begin|end)",
        ]),
    }

    options.fn_force_lambda__regex = code_utils.join_string_by_pipe_char([
        # Any function whose name starts by "get_" or "iam_get_blended_"
        # (those function were rewritten with a specific API for python
        # => we need to force a lambda so that the correct signature is user in the pydef)
        r"get_",
        r"iam_get_blended_"
    ])

    # Add ImGuiID type alias
    options.type_replacements.add_last_replacement(r"^ImGuiID$", "int")

    def postprocess_stub_function(stub_code: str) -> str:
        # Remove iam_ prefix from function names in stubs as well
        r = stub_code.replace("iam_", "")
        r = r.replace("ImVector[float]", "ImVector_float")
        r = r.replace("ImVector[ImVec4]", "ImVector_ImVec4")
        return r

    options.postprocess_stub_function = postprocess_stub_function

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    main()
