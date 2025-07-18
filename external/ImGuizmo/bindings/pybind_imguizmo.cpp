// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#ifdef IMGUI_BUNDLE_WITH_IMGUIZMO
#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/array.h>
#include <nanobind/stl/optional.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/function.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/stl/optional.h>
#include <nanobind/make_iterator.h>
#include <nanobind/trampoline.h>
#include <nanobind/ndarray.h>

#define IMGUI_DEFINE_MATH_OPERATORS
#include "imgui_internal.h"

#include "ImGuizmoPure/ImCurveEditPure.h"
#include "ImGuizmoPure/ImGradientPure.h"
#include "ImGuizmoPure/ImZoomSliderPure.h"
#include "ImGuizmoPure/ImGuizmoPure.h"


namespace nb = nanobind;
using namespace ImGuizmo;


// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// <litgen_glue_code>  // Autogenerated code below! Do not edit!

// </litgen_glue_code> // Autogenerated code end
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE END !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


void py_init_module_imguizmo(nb::module_& m)
{
    using SelectedPoints = ImCurveEdit::SelectedPoints;
    using Range = ImZoomSlider::Range;
    using namespace ImZoomSlider;

    // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    // <litgen_pydef> // Autogenerated code below! Do not edit!
    ////////////////////    <generated_from:ImGuizmoPure.h>    ////////////////////

    { // <namespace ImGuizmo>
        nb::module_ pyNsImGuizmo = m.def_submodule("im_guizmo", "");
        pyNsImGuizmo.def("set_drawlist",
            ImGuizmo::SetDrawlist,
            nb::arg("drawlist") = nb::none(),
            " call inside your own window and before Manipulate() in order to draw gizmo to that window.\n Or pass a specific ImDrawList to draw to (e.g. ImGui::GetForegroundDrawList()).");

        pyNsImGuizmo.def("begin_frame",
            ImGuizmo::BeginFrame, "call BeginFrame right after ImGui_XXXX_NewFrame();");

        pyNsImGuizmo.def("set_im_gui_context",
            ImGuizmo::SetImGuiContext,
            nb::arg("ctx"),
            " this is necessary because when imguizmo is compiled into a dll, and imgui into another\n globals are not shared between them.\n More details at https://stackoverflow.com/questions/19373061/what-happens-to-global-and-static-variables-in-a-shared-library-when-it-is-dynam\n expose method to set imgui context");

        pyNsImGuizmo.def("is_over",
            nb::overload_cast<>(ImGuizmo::IsOver), "return True if mouse cursor is over any gizmo control (axis, plan or screen component)");

        pyNsImGuizmo.def("is_using",
            ImGuizmo::IsUsing, "return True if mouse IsOver or if the gizmo is in moving state");

        pyNsImGuizmo.def("is_using_view_manipulate",
            nb::overload_cast<>(ImGuizmo::IsUsingViewManipulate), "return True if the view gizmo is in moving state");

        pyNsImGuizmo.def("is_view_manipulate_hovered",
            nb::overload_cast<>(ImGuizmo::IsViewManipulateHovered), "only check if your mouse is over the view manipulator - no matter whether it's active or not");

        pyNsImGuizmo.def("is_using_any",
            ImGuizmo::IsUsingAny, "return True if any gizmo is in moving state");

        pyNsImGuizmo.def("enable",
            ImGuizmo::Enable,
            nb::arg("enable"),
            " enable/disable the gizmo. Stay in the state until next call to Enable.\n gizmo is rendered with gray half transparent color when disabled");

        pyNsImGuizmo.def("set_rect",
            ImGuizmo::SetRect, nb::arg("x"), nb::arg("y"), nb::arg("width"), nb::arg("height"));

        pyNsImGuizmo.def("set_orthographic",
            ImGuizmo::SetOrthographic,
            nb::arg("is_orthographic"),
            "default is False");


        auto pyEnumOPERATION =
            nb::enum_<ImGuizmo::OPERATION>(pyNsImGuizmo, "OPERATION", nb::is_arithmetic(), " call it when you want a gizmo\n Needs view and projection matrices.\n matrix parameter is the source matrix (where will be gizmo be drawn) and might be transformed by the function. Return deltaMatrix is optional\n translation is applied in world space")
                .value("translate_x", ImGuizmo::TRANSLATE_X, "")
                .value("translate_y", ImGuizmo::TRANSLATE_Y, "")
                .value("translate_z", ImGuizmo::TRANSLATE_Z, "")
                .value("rotate_x", ImGuizmo::ROTATE_X, "")
                .value("rotate_y", ImGuizmo::ROTATE_Y, "")
                .value("rotate_z", ImGuizmo::ROTATE_Z, "")
                .value("rotate_screen", ImGuizmo::ROTATE_SCREEN, "")
                .value("scale_x", ImGuizmo::SCALE_X, "")
                .value("scale_y", ImGuizmo::SCALE_Y, "")
                .value("scale_z", ImGuizmo::SCALE_Z, "")
                .value("bounds", ImGuizmo::BOUNDS, "")
                .value("scale_xu", ImGuizmo::SCALE_XU, "")
                .value("scale_yu", ImGuizmo::SCALE_YU, "")
                .value("scale_zu", ImGuizmo::SCALE_ZU, "")
                .value("translate", ImGuizmo::TRANSLATE, "")
                .value("rotate", ImGuizmo::ROTATE, "")
                .value("scale", ImGuizmo::SCALE, "")
                .value("scaleu", ImGuizmo::SCALEU, "universal")
                .value("universal", ImGuizmo::UNIVERSAL, "");


        auto pyEnumMODE =
            nb::enum_<ImGuizmo::MODE>(pyNsImGuizmo, "MODE", nb::is_arithmetic(), "")
                .value("local", ImGuizmo::LOCAL, "")
                .value("world", ImGuizmo::WORLD, "");


        pyNsImGuizmo.def("set_alternative_window",
            ImGuizmo::SetAlternativeWindow, nb::arg("window"));

        pyNsImGuizmo.def("push_id",
            nb::overload_cast<const char *>(ImGuizmo::PushID),
            nb::arg("str_id"),
            "push string into the ID stack (will hash string).");

        pyNsImGuizmo.def("push_id",
            nb::overload_cast<const char *, const char *>(ImGuizmo::PushID),
            nb::arg("str_id_begin"), nb::arg("str_id_end"),
            "push string into the ID stack (will hash string).");

        pyNsImGuizmo.def("push_id",
            nb::overload_cast<const void *>(ImGuizmo::PushID),
            nb::arg("ptr_id"),
            "push pointer into the ID stack (will hash pointer).");

        pyNsImGuizmo.def("push_id",
            nb::overload_cast<int>(ImGuizmo::PushID),
            nb::arg("int_id"),
            "push integer into the ID stack (will hash integer).");

        pyNsImGuizmo.def("pop_id",
            ImGuizmo::PopID, "pop from the ID stack.");

        pyNsImGuizmo.def("get_id",
            nb::overload_cast<const char *>(ImGuizmo::GetID),
            nb::arg("str_id"),
            "calculate unique ID (hash of whole ID stack + given parameter). e.g. if you want to query into ImGuiStorage yourself");

        pyNsImGuizmo.def("get_id",
            nb::overload_cast<const char *, const char *>(ImGuizmo::GetID), nb::arg("str_id_begin"), nb::arg("str_id_end"));

        pyNsImGuizmo.def("get_id",
            nb::overload_cast<const void *>(ImGuizmo::GetID), nb::arg("ptr_id"));

        pyNsImGuizmo.def("is_over",
            nb::overload_cast<ImGuizmo::OPERATION>(ImGuizmo::IsOver), nb::arg("op"));

        pyNsImGuizmo.def("set_gizmo_size_clip_space",
            ImGuizmo::SetGizmoSizeClipSpace, nb::arg("value"));

        pyNsImGuizmo.def("allow_axis_flip",
            ImGuizmo::AllowAxisFlip,
            nb::arg("value"),
            " Allow axis to flip\n When True (default), the guizmo axis flip for better visibility\n When False, they always stay along the positive world/local axis");

        pyNsImGuizmo.def("set_axis_limit",
            ImGuizmo::SetAxisLimit,
            nb::arg("value"),
            "Configure the limit where axis are hidden");

        pyNsImGuizmo.def("set_axis_mask",
            ImGuizmo::SetAxisMask,
            nb::arg("x"), nb::arg("y"), nb::arg("z"),
            "Set an axis mask to permanently hide a given axis (True -> hidden, False -> shown)");

        pyNsImGuizmo.def("set_plane_limit",
            ImGuizmo::SetPlaneLimit,
            nb::arg("value"),
            "Configure the limit where planes are hiden");


        auto pyEnumCOLOR =
            nb::enum_<ImGuizmo::COLOR>(pyNsImGuizmo, "COLOR", nb::is_arithmetic(), "")
                .value("direction_x", ImGuizmo::DIRECTION_X, "directionColor[0]")
                .value("direction_y", ImGuizmo::DIRECTION_Y, "directionColor[1]")
                .value("direction_z", ImGuizmo::DIRECTION_Z, "directionColor[2]")
                .value("plane_x", ImGuizmo::PLANE_X, "planeColor[0]")
                .value("plane_y", ImGuizmo::PLANE_Y, "planeColor[1]")
                .value("plane_z", ImGuizmo::PLANE_Z, "planeColor[2]")
                .value("selection", ImGuizmo::SELECTION, "selectionColor")
                .value("inactive", ImGuizmo::INACTIVE, "inactiveColor")
                .value("translation_line", ImGuizmo::TRANSLATION_LINE, "translationLineColor")
                .value("scale_line", ImGuizmo::SCALE_LINE, "")
                .value("rotation_using_border", ImGuizmo::ROTATION_USING_BORDER, "")
                .value("rotation_using_fill", ImGuizmo::ROTATION_USING_FILL, "")
                .value("hatched_axis_lines", ImGuizmo::HATCHED_AXIS_LINES, "")
                .value("text", ImGuizmo::TEXT, "")
                .value("text_shadow", ImGuizmo::TEXT_SHADOW, "")
                .value("count", ImGuizmo::COUNT, "");


        auto pyNsImGuizmo_ClassStyle =
            nb::class_<ImGuizmo::Style>
                (pyNsImGuizmo, "Style", "")
            .def(nb::init<>())
            .def_rw("translation_line_thickness", &ImGuizmo::Style::TranslationLineThickness, "Thickness of lines for translation gizmo")
            .def_rw("translation_line_arrow_size", &ImGuizmo::Style::TranslationLineArrowSize, "Size of arrow at the end of lines for translation gizmo")
            .def_rw("rotation_line_thickness", &ImGuizmo::Style::RotationLineThickness, "Thickness of lines for rotation gizmo")
            .def_rw("rotation_outer_line_thickness", &ImGuizmo::Style::RotationOuterLineThickness, "Thickness of line surrounding the rotation gizmo")
            .def_rw("scale_line_thickness", &ImGuizmo::Style::ScaleLineThickness, "Thickness of lines for scale gizmo")
            .def_rw("scale_line_circle_size", &ImGuizmo::Style::ScaleLineCircleSize, "Size of circle at the end of lines for scale gizmo")
            .def_rw("hatched_axis_line_thickness", &ImGuizmo::Style::HatchedAxisLineThickness, "Thickness of hatched axis lines")
            .def_rw("center_circle_size", &ImGuizmo::Style::CenterCircleSize, "Size of circle at the center of the translate/scale gizmo")
            ;


        pyNsImGuizmo.def("get_style",
            ImGuizmo::GetStyle, nb::rv_policy::reference);
        auto pyNsImGuizmo_ClassMatrix16 =
            nb::class_<ImGuizmo::Matrix16>
                (pyNsImGuizmo, "Matrix16", "")
            .def_prop_ro("values",
                [](ImGuizmo::Matrix16 &self) -> nb::ndarray<float, nb::numpy, nb::shape<16>, nb::c_contig>
                {
                    return self.values;
                },
                "")
            .def(nb::init<>())
            .def(nb::init<const std::array<float, 16> &>(),
                nb::arg("v"))
            ;


        auto pyNsImGuizmo_ClassMatrix6 =
            nb::class_<ImGuizmo::Matrix6>
                (pyNsImGuizmo, "Matrix6", "")
            .def_prop_ro("values",
                [](ImGuizmo::Matrix6 &self) -> nb::ndarray<float, nb::numpy, nb::shape<6>, nb::c_contig>
                {
                    return self.values;
                },
                "")
            .def(nb::init<>())
            .def(nb::init<const std::array<float, 6> &>(),
                nb::arg("v"))
            ;


        auto pyNsImGuizmo_ClassMatrix3 =
            nb::class_<ImGuizmo::Matrix3>
                (pyNsImGuizmo, "Matrix3", "")
            .def_prop_ro("values",
                [](ImGuizmo::Matrix3 &self) -> nb::ndarray<float, nb::numpy, nb::shape<3>, nb::c_contig>
                {
                    return self.values;
                },
                "")
            .def(nb::init<>())
            .def(nb::init<const std::array<float, 3> &>(),
                nb::arg("v"))
            ;


        auto pyNsImGuizmo_ClassMatrixComponents =
            nb::class_<ImGuizmo::MatrixComponents>
                (pyNsImGuizmo, "MatrixComponents", "")
            .def(nb::init<>()) // implicit default constructor
            .def_rw("translation", &ImGuizmo::MatrixComponents::Translation, "")
            .def_rw("rotation", &ImGuizmo::MatrixComponents::Rotation, "")
            .def_rw("scale", &ImGuizmo::MatrixComponents::Scale, "")
            ;


        pyNsImGuizmo.def("decompose_matrix_to_components",
            nb::overload_cast<const ImGuizmo::Matrix16 &>(ImGuizmo::DecomposeMatrixToComponents), nb::arg("matrix"));

        pyNsImGuizmo.def("recompose_matrix_from_components",
            nb::overload_cast<const ImGuizmo::MatrixComponents &>(ImGuizmo::RecomposeMatrixFromComponents), nb::arg("matrix_components"));

        pyNsImGuizmo.def("draw_cubes",
            nb::overload_cast<const ImGuizmo::Matrix16 &, const ImGuizmo::Matrix16 &, const std::vector<ImGuizmo::Matrix16> &>(ImGuizmo::DrawCubes), nb::arg("view"), nb::arg("projection"), nb::arg("matrices"));

        pyNsImGuizmo.def("draw_grid",
            nb::overload_cast<const ImGuizmo::Matrix16 &, const ImGuizmo::Matrix16 &, const ImGuizmo::Matrix16 &, const float>(ImGuizmo::DrawGrid), nb::arg("view"), nb::arg("projection"), nb::arg("matrix"), nb::arg("grid_size"));

        pyNsImGuizmo.def("manipulate",
            nb::overload_cast<const ImGuizmo::Matrix16 &, const ImGuizmo::Matrix16 &, ImGuizmo::OPERATION, ImGuizmo::MODE, ImGuizmo::Matrix16 &, std::optional<ImGuizmo::Matrix16>, std::optional<ImGuizmo::Matrix3>, std::optional<ImGuizmo::Matrix6>, std::optional<ImGuizmo::Matrix3>>(ImGuizmo::Manipulate),
            nb::arg("view"), nb::arg("projection"), nb::arg("operation"), nb::arg("mode"), nb::arg("object_matrix"), nb::arg("delta_matrix").none() = nb::none(), nb::arg("snap").none() = nb::none(), nb::arg("local_bounds").none() = nb::none(), nb::arg("bounds_snap").none() = nb::none(),
            "Manipulate may change the objectMatrix parameter (return True if modified)");

        pyNsImGuizmo.def("view_manipulate",
            nb::overload_cast<ImGuizmo::Matrix16 &, float, ImVec2, ImVec2, ImU32>(ImGuizmo::ViewManipulate),
            nb::arg("view"), nb::arg("length"), nb::arg("position"), nb::arg("size"), nb::arg("background_color"),
            "\n Please note that this cubeview is patented by Autodesk : https://patents.google.com/patent/US7782319B2/en\n It seems to be a defensive patent in the US. I don't think it will bring troubles using it as\n other software are using the same mechanics. But just in case, you are now warned!\n\n ViewManipulate may change the view parameter");

        pyNsImGuizmo.def("view_manipulate",
            nb::overload_cast<ImGuizmo::Matrix16 &, const ImGuizmo::Matrix16 &, ImGuizmo::OPERATION, ImGuizmo::MODE, ImGuizmo::Matrix16 &, float, ImVec2, ImVec2, ImU32>(ImGuizmo::ViewManipulate),
            nb::arg("view"), nb::arg("projection"), nb::arg("operation"), nb::arg("mode"), nb::arg("matrix"), nb::arg("length"), nb::arg("position"), nb::arg("size"), nb::arg("background_color"),
            " use this version if you did not call Manipulate before, and you are just using ViewManipulate.\n ViewManipulate may change the view parameter!");
    } // </namespace ImGuizmo>
    ////////////////////    </generated_from:ImGuizmoPure.h>    ////////////////////

    // </litgen_pydef> // Autogenerated code end
    // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE END !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
}
#endif // IMGUI_BUNDLE_WITH_IMGUIZMO
