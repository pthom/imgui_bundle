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


// ============================================================================
// Hairy conversions between MatrixXX and numpy arrays, with shared memory
// (inspired by my previous work on cvnp (https://github.com/pthom/cvnp)
// ============================================================================

// ----------------------------------------------------------------------------
// Part 1 : Conversion utilities
// ----------------------------------------------------------------------------
namespace matrix_to_numpy
{
    template<int N>
    std::vector<size_t> matrix_shape()
    {
        // we will transcribe a Matrix16 into a 4x4 matrix on python side
        // But the others will stay flat
        if (N == 3)
            return {3};
        else if (N == 6)
            return {6};
        else if (N == 16)
            return {4, 4};
        else
            throw std::runtime_error("pybind_imguizmo.cpp: matrix_to_numpy::matrix_shape => bad N");
    }

    template<int N>
    std::vector<int64_t> matrix_strides()
    {
        nb::ssize_t s = sizeof(float);
        if ((N == 3) || (N == 6))
            return {s};
        else if (N == 16)
            return { 4 * s, s };
        else
            throw std::runtime_error("pybind_imguizmo.cpp: matrix_to_numpy::matrix_strides => bad N");
    }

    template<int N>
    nb::ndarray<> matrix_to_nparray(const MatrixFixedSize<N>& m)
    {
        std::vector<size_t> shape = matrix_shape<N>();
        std::vector<int64_t> strides = matrix_strides<N>();

        // old pybind11 code
        // static std::string float_numpy_str = nb::format_descriptor<float>::format();
        // static auto dtype_float = nb::dtype(float_numpy_str);
        // return nb::array(dtype_float, shape, strides, m.values);

        // new nanobind code:
        // ndarray constructor signature:
        //        ndarray(VoidPtr data,
        //            size_t ndim,
        //            const size_t *shape,
        //            handle owner = { },
        //            const int64_t *strides = nullptr,
        //            dlpack::dtype dtype = nanobind::dtype<Scalar>(),
        //            int device_type = DeviceType,
        //            int device_id = 0,
        //            char order = Order)
        nb::ndarray<> a(
            const_cast<void*>(static_cast<const void*>(m.values)), // Ensure non-const void*
            shape.size(), // ndim
            shape.data(), // shape
            {}, // owner
            strides.data(), // strides as initializer_list
            nb::dtype<float>()
        );
        return a;
    }

    template<int N>
    MatrixFixedSize<N> nparray_to_matrix(nb::ndarray<>& a)
    {
        MatrixFixedSize<N> r;

        if (a.itemsize() != sizeof(float))
            throw std::runtime_error("pybind_imguizmo.cpp::nparray_to_matrix / only numpy arrays of type np.float32 are supported!");

        // Check input array type

        // old pybind11 code
        //        if (a.dtype().kind() != nb::format_descriptor<float>::c)
        //            throw std::runtime_error("pybind_imguizmo.cpp::nparray_to_matrix / only numpy arrays of type np.float32 are supported!");

        // new nanobind code:
        if (! (a.dtype().code == static_cast<uint8_t>(nb::dlpack::dtype_code::Float) && a.dtype().bits / 8 == sizeof(float)))
            throw std::runtime_error("pybind_imguizmo.cpp::nparray_to_matrix / only numpy arrays of type np.float32 are supported!");

        // Check input array total length
        if (a.size() != N)
            throw std::runtime_error("pybind_imguizmo.cpp::nparray_to_matrix / bad size!");

        // ...and then copy its values
        const float* np_values_ptr = static_cast<const float*>(a.data());
        for (int i = 0; i < N; ++i)
            r.values[i] = np_values_ptr[i];

        return r;
    }

}

// ----------------------------------------------------------------------------
// Part 1 : Type casters numpy.array <=> MatrixXX
// ----------------------------------------------------------------------------
namespace nanobind
{
    namespace detail
    {
        template<int N>
        struct type_caster<MatrixFixedSize<N>>
        {
            NB_TYPE_CASTER(MatrixFixedSize<N>, const_name("MatrixFixedSize"))

            bool from_python(handle src, uint8_t flags, cleanup_list *cleanup) noexcept
            {
                // Check if the source is a numpy.ndarray
                if (!isinstance<ndarray<>>(src))
                {
                    PyErr_WarnFormat(PyExc_Warning, 1, "nanobind: MatrixFixedSize type_caster from_python: expected a numpy.ndarray");
                    return false;
                }

                try
                {
                    auto a = nb::cast<ndarray<>>(src);
                    // Store the conversion into the member
                    // value (of type MatrixFixedSize<N>)
                    value = matrix_to_numpy::nparray_to_matrix<N>(a);
                    return true;
                }
                catch (const std::runtime_error& e) {
                    PyErr_WarnFormat(PyExc_Warning, 1, "nanobind: exception in MatrixFixedSize type_caster from_python: %s", e.what());
                    return false;
                }
            }

            static handle from_cpp(const MatrixFixedSize<N> &m, rv_policy policy, cleanup_list *cleanup) noexcept
            {
                try {
                    ndarray<> a = matrix_to_numpy::matrix_to_nparray<N>(m); // This succeeds
                    // inspired by ndarray.h caster:
                    // We need to call ndarray_export to export a python handle for the ndarray
                    auto r = ndarray_export(
                        a.handle(), // internal array handle
                        nb::numpy::value, // framework (i.e numpy, pytorch, etc)
                        policy,
                        cleanup);
                    return r;
                }
                catch (const std::runtime_error& e) {
                    PyErr_WarnFormat(PyExc_Warning, 1, "nanobind: exception in MatrixFixedSize type_caster from_cpp: %s", e.what());
                    return {};
                }
            }
        };
    }
}


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
    ////////////////////    <generated_from:Editable.h>    ////////////////////
    auto pyClassEditable_SelectedPoints =
        nb::class_<Editable<SelectedPoints>>
            (m, "Editable_SelectedPoints", " Editable: a simple structure to extend ImGui's policy of \"returning True when changed\",\n by adding with a modified return value to the functions output")
        .def(nb::init<const SelectedPoints &, bool>(),
            nb::arg("value"), nb::arg("edited") = false)
        .def("__bool__",
            &Editable<SelectedPoints>::operator bool, "Invoke this operator to check for user modification")
        .def_rw("value", &Editable<SelectedPoints>::Value, "")
        .def_rw("edited", &Editable<SelectedPoints>::Edited, "")
        ;
    auto pyClassEditable_int =
        nb::class_<Editable<int>>
            (m, "Editable_int", " Editable: a simple structure to extend ImGui's policy of \"returning True when changed\",\n by adding with a modified return value to the functions output")
        .def(nb::init<const int &, bool>(),
            nb::arg("value"), nb::arg("edited") = false)
        .def("__bool__",
            &Editable<int>::operator bool, "Invoke this operator to check for user modification")
        .def_rw("value", &Editable<int>::Value, "")
        .def_rw("edited", &Editable<int>::Edited, "")
        ;
    auto pyClassEditable_Matrix16 =
        nb::class_<Editable<Matrix16>>
            (m, "Editable_Matrix16", " Editable: a simple structure to extend ImGui's policy of \"returning True when changed\",\n by adding with a modified return value to the functions output")
        .def(nb::init<const Matrix16 &, bool>(),
            nb::arg("value"), nb::arg("edited") = false)
        .def("__bool__",
            &Editable<Matrix16>::operator bool, "Invoke this operator to check for user modification")
        .def_rw("value", &Editable<Matrix16>::Value, "")
        .def_rw("edited", &Editable<Matrix16>::Edited, "")
        ;
    auto pyClassEditable_Range =
        nb::class_<Editable<Range>>
            (m, "Editable_Range", " Editable: a simple structure to extend ImGui's policy of \"returning True when changed\",\n by adding with a modified return value to the functions output")
        .def(nb::init<const Range &, bool>(),
            nb::arg("value"), nb::arg("edited") = false)
        .def("__bool__",
            &Editable<Range>::operator bool, "Invoke this operator to check for user modification")
        .def_rw("value", &Editable<Range>::Value, "")
        .def_rw("edited", &Editable<Range>::Edited, "")
        ;
    ////////////////////    </generated_from:Editable.h>    ////////////////////


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


        pyNsImGuizmo.def("set_id",
            ImGuizmo::SetID, nb::arg("id"));

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
            ImGuizmo::GetStyle);
        auto pyNsImGuizmo_ClassMatrixComponents =
            nb::class_<ImGuizmo::MatrixComponents>
                (pyNsImGuizmo, "MatrixComponents", "")
            .def(nb::init<>()) // implicit default constructor
            .def_rw("translation", &ImGuizmo::MatrixComponents::Translation, "")
            .def_rw("rotation", &ImGuizmo::MatrixComponents::Rotation, "")
            .def_rw("scale", &ImGuizmo::MatrixComponents::Scale, "")
            ;


        pyNsImGuizmo.def("decompose_matrix_to_components",
            nb::overload_cast<const Matrix16 &>(ImGuizmo::DecomposeMatrixToComponents), nb::arg("matrix"));

        pyNsImGuizmo.def("recompose_matrix_from_components",
            nb::overload_cast<const ImGuizmo::MatrixComponents &>(ImGuizmo::RecomposeMatrixFromComponents), nb::arg("matrix_components"));

        pyNsImGuizmo.def("draw_cubes",
            nb::overload_cast<const Matrix16 &, const Matrix16 &, const std::vector<Matrix16> &>(ImGuizmo::DrawCubes), nb::arg("view"), nb::arg("projection"), nb::arg("matrices"));

        pyNsImGuizmo.def("draw_grid",
            nb::overload_cast<const Matrix16 &, const Matrix16 &, const Matrix16 &, const float>(ImGuizmo::DrawGrid), nb::arg("view"), nb::arg("projection"), nb::arg("matrix"), nb::arg("grid_size"));

        pyNsImGuizmo.def("manipulate",
            nb::overload_cast<const Matrix16 &, const Matrix16 &, ImGuizmo::OPERATION, ImGuizmo::MODE, const Matrix16 &, std::optional<Matrix16>, std::optional<Matrix3>, std::optional<Matrix6>, std::optional<Matrix3>>(ImGuizmo::Manipulate),
            nb::arg("view"), nb::arg("projection"), nb::arg("operation"), nb::arg("mode"), nb::arg("object_matrix"), nb::arg("delta_matrix") = nb::none(), nb::arg("snap") = nb::none(), nb::arg("local_bounds") = nb::none(), nb::arg("bounds_snap") = nb::none(),
            " Manipulate may change the objectMatrix parameter:\n if it was changed, it will return (True, newObjectMatrix)");

        pyNsImGuizmo.def("view_manipulate",
            nb::overload_cast<const Matrix16 &, float, ImVec2, ImVec2, ImU32>(ImGuizmo::ViewManipulate),
            nb::arg("view"), nb::arg("length"), nb::arg("position"), nb::arg("size"), nb::arg("background_color"),
            "\n Please note that this cubeview is patented by Autodesk : https://patents.google.com/patent/US7782319B2/en\n It seems to be a defensive patent in the US. I don't think it will bring troubles using it as\n other software are using the same mechanics. But just in case, you are now warned!\n\n ViewManipulate may change the view parameter: if it was changed, it will return (True, newView)");

        pyNsImGuizmo.def("view_manipulate",
            nb::overload_cast<const Matrix16 &, const Matrix16 &, ImGuizmo::OPERATION, ImGuizmo::MODE, Matrix16 &, float, ImVec2, ImVec2, ImU32>(ImGuizmo::ViewManipulate),
            nb::arg("view"), nb::arg("projection"), nb::arg("operation"), nb::arg("mode"), nb::arg("matrix"), nb::arg("length"), nb::arg("position"), nb::arg("size"), nb::arg("background_color"),
            " use this version if you did not call Manipulate before and you are just using ViewManipulate\n ViewManipulate may change the view parameter: if it was changed, it will return (True, newView)");
    } // </namespace ImGuizmo>
    ////////////////////    </generated_from:ImGuizmoPure.h>    ////////////////////

    // </litgen_pydef> // Autogenerated code end
    // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE END !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
}
#endif // IMGUI_BUNDLE_WITH_IMGUIZMO
